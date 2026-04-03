import platform
import shutil
import subprocess


SUPPORTED = {
    "apt":  "Ubuntu / Debian",
    "dnf":  "Fedora / RHEL",
    "brew": "macOS",
}


def detect_package_manager() -> tuple[str, str] | None:
    """
    Returns (manager, label) or None if unsupported.
    """
    for manager, label in SUPPORTED.items():
        if shutil.which(manager):
            return manager, label
    return None


def is_installed(package_name: str) -> bool:
    """
    Check if a package is already installed on the system.
    Works across apt, dnf, and brew environments.
    """
    # Try 'which' first for binaries
    if shutil.which(package_name):
        return True

    # apt/dpkg check
    try:
        result = subprocess.run(
            ["dpkg", "-s", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and "Status: install ok installed" in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # rpm/dnf check
    try:
        result = subprocess.run(
            ["rpm", "-q", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # brew check
    try:
        result = subprocess.run(
            ["brew", "list", "--formula", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    return False
