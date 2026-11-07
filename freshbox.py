#!/usr/bin/env python3

import argparse
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from installer.detect import detect_package_manager
from installer.packages import load_packages
from installer.runner import install_package, Status, update_package_manager


console = Console()

BANNER = r"""
 _   _  _____ ___  __  __ ____
| | | |/ ____/ _ \|  \/  |  _ \
| | | | |   | | | | \  / | |_) |
| | | | |   | | | | |\/| |  __/
| |_| | |___| |_| | |  | | |
 \___/ \_____\___/|_|  |_|_|

 _____              _     _
|  ___| __ ___  ___| |__ | |__   _____  __
| |_ | '__/ _ \/ __| '_ \| '_ \ / _ \ \/ /
|  _|| | |  __/\__ \ | | | |_) | (_) >  <
|_|  |_|  \___||___/_| |_|_.__/ \___/_/\_\

"""

TAGLINE    = "made in earth, by humans, for humans"
LOADING_MSG = "running the scripts you are too lazy to run.... apparently someone is too lazy for sudo update..."
VERSION    = "v1.1.0"

CONFIG_PATH = Path(__file__).parent / "config" / "packages.toml"

# One accent color per pack so the banner changes with each selection.
PACK_COLORS = {
    "stock":        "white",
    "monitors":     "red",
    "devtools":     "green",
    "shell":        "blue",
    "terminal":     "magenta",
    "cybersecurity":"bright_red",
    "webdev":       "bright_blue",
    "circuitdev":   "bright_magenta",
    "science":      "bright_cyan",
    "electronics":  "yellow",
    "privacy":      "bright_magenta",
    "sysadmin":     "bright_yellow",
    "arch":         "bright_blue",
    "alpine":       "bright_cyan",
    "gentoo":       "bright_red",
    "void":         "green",
    "windows":      "cyan",
    "freebsd":      "bright_green",
    "openbsd":      "bright_green",
    "netbsd":       "bright_green",
}
DEFAULT_COLOR = "red"


def print_banner(color=DEFAULT_COLOR):
    console.print(f"[bold {color}]{BANNER}[/bold {color}]")
    console.print(f"[bold white]  {TAGLINE}[/bold white]")
    console.print(f"[dim]  {VERSION}[/dim]\n")


def print_loading():
    console.print(f"[dim italic]{LOADING_MSG}[/dim italic]\n")
    time.sleep(1.5)


def print_plan(categories, manager_label, dry_run=False, color=DEFAULT_COLOR):
    mode = "dry run (no changes will be made)" if dry_run else "full install"
    packs = ", ".join(c.key for c in categories)
    console.print(Panel(
        f"[bold]detected:[/bold] [green]{manager_label}[/green]\n"
        f"[bold]mode:[/bold] {mode}\n"
        f"[bold]packs:[/bold] {packs}\n"
        f"[bold]packages:[/bold] {sum(len(c.packages) for c in categories)} across {len(categories)} categories",
        title="[bold white]freshbox[/bold white]",
        border_style=color,
    ))
    console.print()


def print_summary(results, dry_run=False):
    installed = [r for r in results if r.status == Status.INSTALLED]
    skipped   = [r for r in results if r.status == Status.SKIPPED]
    failed    = [r for r in results if r.status == Status.FAILED]

    verb = "would install" if dry_run else "installed"
    fail_verb = "would fail" if dry_run else "failed"

    table = Table(title="install report", border_style="dim", show_lines=True)
    table.add_column("package",  style="white",  no_wrap=True)
    table.add_column("status",   justify="center")
    table.add_column("notes",    style="dim")

    for r in results:
        if r.status == Status.INSTALLED:
            table.add_row(r.package, "[bold green]would install[/bold green]" if dry_run else "[bold green]installed[/bold green]", "")
        elif r.status == Status.SKIPPED:
            table.add_row(r.package, "[yellow]skipped[/yellow]", "already present")
        else:
            table.add_row(r.package, f"[bold red]{fail_verb}[/bold red]", r.error or "unknown error")

    console.print()
    console.print(table)
    console.print()
    console.print(
        f"  [green]{len(installed)} {verb}[/green]  "
        f"[yellow]{len(skipped)} skipped[/yellow]  "
        f"[red]{len(failed)} {fail_verb}[/red]"
    )

    if failed:
        console.print("\n[dim]failed packages can be retried manually.[/dim]")

    console.print("\n[bold red]entropy writes the final patch.[/bold red]\n")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="freshbox",
        description="automated setup script for a fresh OS.",
    )
    parser.add_argument("--version", action="version", version=f"freshbox {VERSION}")
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="show what would be installed without installing anything",
    )
    parser.add_argument(
        "-c", "--category",
        action="append",
        metavar="KEY",
        help="install only the given category (repeatable; defaults to all)",
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="list all packages by category and exit",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show install commands as they run",
    )
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="skip refreshing package manager indexes before installing",
    )
    return parser


def print_list(categories):
    table = Table(title="available packages", border_style="dim", show_lines=True)
    table.add_column("category", style="white", no_wrap=True)
    table.add_column("package",  style="white", no_wrap=True)
    table.add_column("apt",      style="dim")
    table.add_column("dnf",      style="dim")
    table.add_column("brew",     style="dim")
    table.add_column("notes",    style="dim")

    for cat in categories:
        for pkg in cat.packages:
            notes = []
            if pkg.apt_ppa:
                notes.append(f"ppa: {pkg.apt_ppa}")
            for mgr in ("apt", "dnf", "brew"):
                url = getattr(pkg, f"{mgr}_script", None)
                if url:
                    notes.append(f"{mgr} script: {url}")
            table.add_row(
                cat.label,
                pkg.name,
                pkg.apt,
                pkg.dnf,
                pkg.brew,
                " | ".join(notes),
            )

    console.print(table)
    console.print()


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.list:
        print_loading()

    # load packages
    try:
        categories = load_packages(CONFIG_PATH)
    except FileNotFoundError:
        print_banner()
        console.print(f"[bold red]error:[/bold red] config not found: {CONFIG_PATH}")
        raise SystemExit(1)
    except Exception as exc:
        print_banner()
        console.print(f"[bold red]error:[/bold red] failed to load config: {exc}")
        raise SystemExit(1)

    # category filter
    if args.category:
        valid = {c.key for c in categories}
        bad = [key for key in args.category if key not in valid]
        if bad:
            print_banner()
            console.print(f"[bold red]error:[/bold red] unknown category/categories: {', '.join(bad)}")
            console.print(f"[dim]available: {', '.join(sorted(valid))}[/dim]")
            raise SystemExit(1)
        categories = [c for c in categories if c.key in args.category]
        if not categories:
            print_banner()
            console.print("[bold red]error:[/bold red] no categories selected.")
            raise SystemExit(1)

    # list mode: show every package (of selected categories) and exit
    if args.list:
        print_banner()
        print_list(categories)
        return

    # detect OS
    result = detect_package_manager()
    if result is None:
        print_banner()
        console.print("[bold red]error:[/bold red] unsupported package manager. freshbox supports apt, dnf, brew, nix, zypper, pacman, apk, yum, emerge, xbps, snap, flatpak, winget, chocolatey, pkg, and pkgin.")
        raise SystemExit(1)

    manager, manager_label = result

    # pick a banner color from the first selected pack so it changes per pack
    banner_color = PACK_COLORS.get(categories[0].key, DEFAULT_COLOR) if categories else DEFAULT_COLOR
    print_banner(banner_color)

    # show plan
    print_plan(categories, manager_label, args.dry_run, banner_color)

    # refresh package indexes (skipped in dry-run or with --no-update)
    if not args.dry_run and not args.no_update:
        with Progress(
            SpinnerColumn(style="red"),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("refreshing package indexes...", total=None)
            ok, err = update_package_manager(manager)
            progress.remove_task(task)
        if ok:
            console.print("[green]package indexes refreshed[/green]")
        else:
            console.print(f"[yellow]warning:[/yellow] index refresh failed: {err}  (continuing anyway)")
        console.print()

    # run installs
    all_results = []

    for category in categories:
        console.print(f"[bold white]{category.label}[/bold white]")

        with Progress(
            SpinnerColumn(style="red"),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            for pkg in category.packages:
                action = "checking" if args.dry_run else "installing"
                task = progress.add_task(f"  {action} {pkg.name}...", total=None)
                res = install_package(pkg, manager, dry_run=args.dry_run, verbose=args.verbose)
                all_results.append(res)
                progress.remove_task(task)

                if res.status == Status.INSTALLED:
                    msg = f"  [green]{'would install' if args.dry_run else 'installed'}[/green]  {pkg.name}"
                    if args.dry_run and res.plan:
                        msg += f"  [dim]{res.plan}[/dim]"
                    console.print(msg)
                elif res.status == Status.SKIPPED:
                    console.print(f"  [yellow]skipped[/yellow]   {pkg.name}")
                else:
                    console.print(f"  [red]failed[/red]    {pkg.name}  [dim]{res.error}[/dim]")

        console.print()

    print_summary(all_results, args.dry_run)


if __name__ == "__main__":
    main()
