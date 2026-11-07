# UCOMP Freshbox

automated setup script for a fresh OS. installs everything you actually need on a new machine.

because typing `apt install` forty times is not a personality.

---

## supported systems

- Ubuntu / Debian (apt)
- Fedora / RHEL (dnf)
- macOS (brew)
- NixOS / nix (nix)
- openSUSE / SUSE (zypper)
- Arch Linux / Manjaro (pacman)
- Alpine Linux (apk)
- RHEL / CentOS legacy (yum)
- Gentoo (emerge)
- Void Linux (xbps)
- Snap (universal)
- Flatpak (universal)
- Windows (winget / chocolatey)
- FreeBSD / OpenBSD (pkg)
- NetBSD (pkgin)

---

## what it installs

| pack | tools |
| --- | --- |
| stock / regular | git, curl, wget, make, gcc, vim, nano, zip, tar, rsync, ssh, tree, jq, fd, ripgrep, bat, eza, duf, ncdu |
| system monitors | htop, btop, fastfetch |
| dev tools | git, curl, wget, make, gcc, nodejs, npm, go, rust, cargo, docker |
| shell | zsh, fzf, starship |
| terminal apps | tmux, neovim, bat, eza |
| cybersecurity | nmap, wireshark, metasploit, aircrack-ng, john, hashcat, burpsuite, gobuster, sqlmap, hydra, tcpdump, netcat, amass, ffuf, nuclei, mitmproxy |
| web development | nodejs, npm, yarn, pnpm, php, composer, python3, pip, ruby, go, rust, docker, nginx, apache2, certbot, postgresql, mysql, redis |
| circuit design | kicad, ngspice, gtkwave, verilator, iverilog, openocd, stlink, picocom, minicom |
| science | octave, scilab, gnuplot, numpy, scipy, matplotlib, pandas, sympy, sagemath, gmsh |
| electrical engineering | kicad, ngspice, verilator, iverilog, ghdl, yosys, nextpnr, openocd, sigrok, pulseview |
| privacy & anonymity | tor, torsocks, gnupg, veracrypt, keepassxc, bleachbit |
| system administration | ansible, terraform, kubectl, helm, fail2ban, auditd |

already installed packages are skipped. one failure does not stop the rest.

---

## usage

```bash
git clone https://github.com/freedomwarriorx86/freshbox
cd freshbox
pip install -r requirements.txt
python freshbox.py
```

needs sudo for apt and dnf installs. it will ask.

### cli options

| option | description |
| --- | --- |
| `-n, --dry-run` | show what would be installed without installing anything |
| `-c, --category KEY` | install only the given category (repeatable; defaults to all) |
| `-l, --list` | list all packages by category and exit |
| `-v, --verbose` | print each install command as it runs |
| `--no-update` | skip refreshing package manager indexes before installing |
| `--version` | print version and exit |

examples:

```bash
# preview everything that would be installed
python freshbox.py --dry-run

# install only shell and terminal tools
python freshbox.py -c shell -c terminal

# see all available packages
python freshbox.py --list

# verbose install with no index refresh
python freshbox.py -v --no-update
```

categories: `stock`, `monitors`, `devtools`, `shell`, `terminal`, `cybersecurity`, `webdev`, `circuitdev`, `science`, `electronics`, `privacy`, `sysadmin`.

---

## adding packages

open `config/packages.toml` and add an entry to any category. format is simple.

```toml
{ name = "toolname", apt = "apt-package-name", dnf = "dnf-package-name", brew = "brew-package-name" }
```

---

*UCOMP. made in earth, for humans.*
