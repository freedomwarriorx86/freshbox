# UCOMP Freshbox

automated setup script for a fresh OS. installs everything you actually need on a new machine.

because typing `apt install` forty times is not a personality.

---

## supported systems

- Ubuntu / Debian (apt)
- Fedora / RHEL (dnf)
- macOS (brew)

---

## what it installs

| category | tools |
|---|---|
| system monitors | htop, btop, fastfetch |
| dev tools | git, curl, wget, make, build-essential |
| shell | zsh, fzf, starship |
| terminal apps | tmux, neovim, bat, eza |

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

---

## adding packages

open `config/packages.toml` and add an entry to any category. format is simple.

```toml
{ name = "toolname", apt = "apt-package-name", dnf = "dnf-package-name", brew = "brew-package-name" }
```

---

*UCOMP. made in earth, for humans.*
