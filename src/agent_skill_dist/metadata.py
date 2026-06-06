from __future__ import annotations

import json
from datetime import UTC, datetime
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

INSTALL_METADATA_FILE = ".agent-skill-install.json"


def get_distribution_version(distribution: str) -> str | None:
    try:
        return importlib_metadata.version(distribution)
    except importlib_metadata.PackageNotFoundError:
        return None


def build_install_metadata(
    *,
    distribution: str,
    package: str,
    package_version: str | None,
    skill_name: str,
    installed_at: datetime,
) -> dict[str, Any]:
    if installed_at.tzinfo is None:
        installed_at = installed_at.replace(tzinfo=UTC)

    return {
        "source": "python-package",
        "distribution": distribution,
        "package": package,
        "package_version": package_version,
        "skill_name": skill_name,
        "installed_by": "agent-skill-dist",
        "installed_at": installed_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
    }


def read_install_metadata(destination: Path) -> dict[str, Any] | None:
    metadata_path = destination / INSTALL_METADATA_FILE
    if not metadata_path.exists():
        return None
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return data
