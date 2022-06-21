"""
Contains some data we use throughout this project.
Typically this file just contains the project root.
"""
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent
