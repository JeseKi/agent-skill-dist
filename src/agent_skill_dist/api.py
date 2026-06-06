from __future__ import annotations

import json
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from agent_skill_dist.exceptions import SkillAlreadyExists
from agent_skill_dist.metadata import (
    INSTALL_METADATA_FILE,
    build_install_metadata,
    get_distribution_version,
    read_install_metadata,
)
from agent_skill_dist.resources import (
    copy_traversable_tree,
    get_bundled_skill,
    validate_bundled_skill,
)
from agent_skill_dist.targets import resolve_destination
from agent_skill_dist.types import SkillInstallStatus


def install_bundled_skill(
    *,
    package: str,
    distribution: str,
    resource_root: str,
    skill_name: str,
    package_version: str | None = None,
    target: str = "user",
    output: str | Path | None = None,
    yes: bool = False,
) -> SkillInstallStatus:
    """把内置 skill 安装到兼容 Codex 约定的 skill 目录。"""

    bundled_skill = get_bundled_skill(package, resource_root, skill_name)
    validate_bundled_skill(bundled_skill, skill_name)
    destination = resolve_destination(
        target=target,
        output=output,
        skill_name=skill_name,
    )
    bundled_version = package_version or get_distribution_version(distribution)

    if destination.exists() and not yes:
        raise SkillAlreadyExists(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = Path(
        tempfile.mkdtemp(
            prefix=f".{skill_name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
    )
    try:
        copy_traversable_tree(bundled_skill, temp_path)
        metadata = build_install_metadata(
            distribution=distribution,
            package=package,
            package_version=bundled_version,
            skill_name=skill_name,
            installed_at=datetime.now(UTC),
        )
        (temp_path / INSTALL_METADATA_FILE).write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        if destination.exists():
            _remove_existing_destination(destination)
        temp_path.replace(destination)
    except Exception:
        if temp_path.exists():
            shutil.rmtree(temp_path)
        raise

    return skill_status(
        package=package,
        distribution=distribution,
        resource_root=resource_root,
        skill_name=skill_name,
        package_version=package_version,
        target=target,
        output=output,
    )


def skill_status(
    *,
    package: str,
    distribution: str,
    resource_root: str,
    skill_name: str,
    package_version: str | None = None,
    target: str = "user",
    output: str | Path | None = None,
) -> SkillInstallStatus:
    """返回内置 skill 的安装状态。"""

    bundled_skill = get_bundled_skill(package, resource_root, skill_name)
    validate_bundled_skill(bundled_skill, skill_name)

    destination = resolve_destination(
        target=target,
        output=output,
        skill_name=skill_name,
    )
    bundled_version = package_version or get_distribution_version(distribution)
    installed = destination.exists()
    metadata = read_install_metadata(destination)
    installed_version = metadata.get("package_version") if metadata else None
    outdated = installed and installed_version != bundled_version

    return SkillInstallStatus(
        skill_name=skill_name,
        target="output" if output is not None else target,
        destination=destination,
        bundled_version=bundled_version,
        installed_version=installed_version,
        installed=installed,
        outdated=outdated,
        would_overwrite=installed,
        metadata_path=destination / INSTALL_METADATA_FILE,
    )


def _remove_existing_destination(destination: Path) -> None:
    if destination.is_dir():
        shutil.rmtree(destination)
    else:
        destination.unlink()
