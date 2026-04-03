import subprocess
import shutil
from dataclasses import dataclass
from enum import Enum

from installer.detect import is_installed
from installer.packages import Package


class Status(Enum):
    INSTALLED  = "installed"
    SKIPPED    = "skipped"
    FAILED     = "failed"


@dataclass
class Result:
    package: str
    status: Status
    error: str = ""


INSTALL_COMMANDS = {
    "apt":  ["sudo", "apt", "install", "-y"],
    "dnf":  ["sudo", "dnf", "install", "-y"],
    "brew": ["brew", "install"],
}


def _run(cmd: list[str], timeout: int = 120) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode == 0, proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    except Exception as e:
        return False, str(e)


def _add_ppa(ppa: str) -> tuple[bool, str]:
    if not shutil.which("add-apt-repository"):
        ok, err = _run(["sudo", "apt", "install", "-y", "software-properties-common"])
        if not ok:
            return False, f"could not install software-properties-common: {err}"
    ok, err = _run(["sudo", "add-apt-repository", "-y", ppa])
    if not ok:
        return False, f"could not add ppa: {err}"
    ok, err = _run(["sudo", "apt", "update"])
    if not ok:
        return False, f"apt update failed after adding ppa: {err}"
    return True, ""


def _run_script(url: str) -> tuple[bool, str]:
    if not shutil.which("curl"):
        return False, "curl is not installed. install curl first."
    try:
        curl = subprocess.run(
            ["curl", "-sS", url],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if curl.returncode != 0:
            return False, f"failed to fetch install script: {curl.stderr.strip()}"

        proc = subprocess.run(
            ["sh", "-s", "--", "--yes"],
            input=curl.stdout,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return proc.returncode == 0, proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "install script timed out"
    except Exception as e:
        return False, str(e)


def install_package(pkg: Package, manager: str) -> Result:
    if is_installed(pkg.name):
        return Result(package=pkg.name, status=Status.SKIPPED)

    # script-based install (e.g. starship)
    script_url = getattr(pkg, f"{manager}_script", None)
    if script_url:
        ok, err = _run_script(script_url)
        if ok:
            return Result(package=pkg.name, status=Status.INSTALLED)
        return Result(package=pkg.name, status=Status.FAILED, error=err)

    # ppa-based install (apt only)
    if manager == "apt":
        ppa = getattr(pkg, "apt_ppa", None)
        if ppa:
            ok, err = _add_ppa(ppa)
            if not ok:
                return Result(package=pkg.name, status=Status.FAILED, error=err)

    # standard install
    pkg_id = pkg.for_manager(manager)
    if not pkg_id:
        return Result(package=pkg.name, status=Status.FAILED, error=f"no package defined for {manager}")

    cmd = INSTALL_COMMANDS[manager] + [pkg_id]
    ok, err = _run(cmd)
    if ok:
        return Result(package=pkg.name, status=Status.INSTALLED)
    return Result(package=pkg.name, status=Status.FAILED, error=err)