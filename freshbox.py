#!/usr/bin/env python3

import time
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from installer.detect import detect_package_manager
from installer.packages import load_packages
from installer.runner import install_package, Status


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
VERSION    = "v1.0.0"

CONFIG_PATH = Path(__file__).parent / "config" / "packages.toml"


def print_banner():
    console.print(f"[bold red]{BANNER}[/bold red]")
    console.print(f"[bold white]  {TAGLINE}[/bold white]")
    console.print(f"[dim]  {VERSION}[/dim]\n")


def print_loading():
    console.print(f"[dim italic]{LOADING_MSG}[/dim italic]\n")
    time.sleep(1.5)


def print_plan(categories, manager_label):
    console.print(Panel(
        f"[bold]detected:[/bold] [green]{manager_label}[/green]\n"
        f"[bold]mode:[/bold] full install\n"
        f"[bold]packages:[/bold] {sum(len(c.packages) for c in categories)} across {len(categories)} categories",
        title="[bold white]freshbox[/bold white]",
        border_style="red",
    ))
    console.print()


def print_summary(results):
    installed = [r for r in results if r.status == Status.INSTALLED]
    skipped   = [r for r in results if r.status == Status.SKIPPED]
    failed    = [r for r in results if r.status == Status.FAILED]

    table = Table(title="install report", border_style="dim", show_lines=True)
    table.add_column("package",  style="white",  no_wrap=True)
    table.add_column("status",   justify="center")
    table.add_column("notes",    style="dim")

    for r in results:
        if r.status == Status.INSTALLED:
            table.add_row(r.package, "[bold green]installed[/bold green]", "")
        elif r.status == Status.SKIPPED:
            table.add_row(r.package, "[yellow]skipped[/yellow]", "already present")
        else:
            table.add_row(r.package, "[bold red]failed[/bold red]", r.error or "unknown error")

    console.print()
    console.print(table)
    console.print()
    console.print(
        f"  [green]{len(installed)} installed[/green]  "
        f"[yellow]{len(skipped)} skipped[/yellow]  "
        f"[red]{len(failed)} failed[/red]"
    )

    if failed:
        console.print("\n[dim]failed packages can be retried manually.[/dim]")

    console.print("\n[bold red]entropy writes the final patch.[/bold red]\n")


def main():
    print_banner()
    print_loading()

    # detect OS
    result = detect_package_manager()
    if result is None:
        console.print("[bold red]error:[/bold red] unsupported package manager. freshbox supports apt, dnf, and brew.")
        raise SystemExit(1)

    manager, manager_label = result

    # load packages
    categories = load_packages(CONFIG_PATH)

    # show plan
    print_plan(categories, manager_label)

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
                task = progress.add_task(f"  installing {pkg.name}...", total=None)
                res = install_package(pkg, manager)
                all_results.append(res)
                progress.remove_task(task)

                if res.status == Status.INSTALLED:
                    console.print(f"  [green]installed[/green]  {pkg.name}")
                elif res.status == Status.SKIPPED:
                    console.print(f"  [yellow]skipped[/yellow]   {pkg.name}")
                else:
                    console.print(f"  [red]failed[/red]    {pkg.name}  [dim]{res.error}[/dim]")

        console.print()

    print_summary(all_results)


if __name__ == "__main__":
    main()
