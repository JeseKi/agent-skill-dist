from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SkillInstallStatus:
    skill_name: str
    target: str
    destination: Path
    bundled_version: str | None
    installed_version: str | None
    installed: bool
    outdated: bool
    would_overwrite: bool
    metadata_path: Path

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "target": self.target,
            "destination": str(self.destination),
            "bundled_version": self.bundled_version,
            "installed_version": self.installed_version,
            "installed": self.installed,
            "outdated": self.outdated,
            "would_overwrite": self.would_overwrite,
            "metadata_path": str(self.metadata_path),
        }
