import tomllib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Package:
    name: str
    apt: str = ""
    dnf: str = ""
    brew: str = ""
    apt_ppa: Optional[str] = None
    apt_script: Optional[str] = None
    dnf_script: Optional[str] = None
    brew_script: Optional[str] = None

    def for_manager(self, manager: str) -> str:
        return getattr(self, manager, "")


@dataclass
class Category:
    key: str
    label: str
    packages: list[Package]


def load_packages(config_path: Path) -> list[Category]:
    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    categories = []
    for key, section in data["categories"].items():
        pkgs = [Package(**p) for p in section["packages"]]
        categories.append(Category(key=key, label=section["label"], packages=pkgs))

    return categories