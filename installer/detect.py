import platform
import shutil
import subprocess


SUPPORTED = {
    "apt":        "Ubuntu / Debian",
    "dnf":        "Fedora / RHEL",
    "brew":       "macOS",
    "nix":        "NixOS / nix",
    "zypper":     "openSUSE / SUSE",
    "pacman":     "Arch Linux / Manjaro",
    "apk":        "Alpine Linux",
    "yum":        "RHEL / CentOS (legacy)",
    "emerge":     "Gentoo",
    "xbps":       "Void Linux",
    "snap":       "Snap (universal)",
    "flatpak":    "Flatpak (universal)",
    "winget":     "Windows (winget)",
    "chocolatey": "Windows (chocolatey)",
    "pkg":        "FreeBSD / OpenBSD (pkgng)",
    "pkgin":      "NetBSD (pkgin)",
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

    # nix check
    try:
        result = subprocess.run(
            ["nix-env", "-q", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # zypper / rpm check (rpm already tried above; try zypper search)
    try:
        result = subprocess.run(
            ["zypper", "se", "--installed-only", "--match-exact", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # pacman check
    try:
        result = subprocess.run(
            ["pacman", "-Q", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # apk check
    try:
        result = subprocess.run(
            ["apk", "info", "-e", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # yum check
    try:
        result = subprocess.run(
            ["yum", "list", "installed", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # emerge / gentoo check via portage db
    try:
        result = subprocess.run(
            ["equery", "list", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # xbps check
    try:
        result = subprocess.run(
            ["xbps-query", "-l", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # snap check
    try:
        result = subprocess.run(
            ["snap", "list", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # flatpak check
    try:
        result = subprocess.run(
            ["flatpak", "list", "--application", "--columns=application"],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    # winget check
    try:
        result = subprocess.run(
            ["winget", "list", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name.lower() in result.stdout.lower():
            return True
    except FileNotFoundError:
        pass

    # chocolatey check
    try:
        result = subprocess.run(
            ["choco", "list", "--local-only", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name.lower() in result.stdout.lower():
            return True
    except FileNotFoundError:
        pass

    # FreeBSD / OpenBSD pkg check
    try:
        result = subprocess.run(
            ["pkg", "info", "-e", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # NetBSD pkgin check
    try:
        result = subprocess.run(
            ["pkgin", "list", package_name],
            capture_output=True, text=True
        )
        if result.returncode == 0 and package_name in result.stdout:
            return True
    except FileNotFoundError:
        pass

    return False
