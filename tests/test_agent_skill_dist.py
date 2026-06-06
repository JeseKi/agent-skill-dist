from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_skill_dist import (
    InvalidBundledSkill,
    SkillAlreadyExists,
    SkillNotFound,
    install_bundled_skill,
    skill_status,
)
from agent_skill_dist.metadata import INSTALL_METADATA_FILE

PACKAGE = "demo_cli"
DIST = "demo-cli"
RESOURCE_ROOT = "bundled_skills"
SKILL_NAME = "demo-skill"


@pytest.fixture(autouse=True)
def package_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agent_skill_dist.metadata.importlib_metadata.version",
        lambda distribution: "1.2.3",
    )


def test_status_reports_not_installed_for_output(tmp_path: Path) -> None:
    status = skill_status(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        output=tmp_path,
    )

    assert status.to_dict() == {
        "skill_name": SKILL_NAME,
        "target": "output",
        "destination": str(tmp_path / SKILL_NAME),
        "bundled_version": "1.2.3",
        "installed_version": None,
        "installed": False,
        "outdated": False,
        "would_overwrite": False,
        "metadata_path": str(tmp_path / SKILL_NAME / INSTALL_METADATA_FILE),
    }


def test_fresh_install_copies_skill_and_metadata(tmp_path: Path) -> None:
    status = install_bundled_skill(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        output=tmp_path,
    )

    destination = tmp_path / SKILL_NAME
    assert status.installed is True
    assert status.outdated is False
    assert (destination / "SKILL.md").is_file()
    assert (destination / "references" / "guide.md").read_text(encoding="utf-8")
    metadata = json.loads(
        (destination / INSTALL_METADATA_FILE).read_text(encoding="utf-8")
    )
    assert metadata["source"] == "python-package"
    assert metadata["distribution"] == DIST
    assert metadata["package"] == PACKAGE
    assert metadata["package_version"] == "1.2.3"
    assert metadata["skill_name"] == SKILL_NAME
    assert metadata["installed_by"] == "agent-skill-dist"
    assert metadata["installed_at"].endswith("Z")


def test_existing_destination_requires_yes(tmp_path: Path) -> None:
    install_bundled_skill(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        output=tmp_path,
    )

    with pytest.raises(SkillAlreadyExists):
        install_bundled_skill(
            package=PACKAGE,
            distribution=DIST,
            resource_root=RESOURCE_ROOT,
            skill_name=SKILL_NAME,
            output=tmp_path,
        )


def test_existing_destination_is_replaced_with_yes(tmp_path: Path) -> None:
    destination = tmp_path / SKILL_NAME
    destination.mkdir()
    (destination / "old.txt").write_text("old", encoding="utf-8")

    install_bundled_skill(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        output=tmp_path,
        yes=True,
    )

    assert not (destination / "old.txt").exists()
    assert (destination / "SKILL.md").is_file()


def test_repo_target_uses_current_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    status = install_bundled_skill(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        target="repo",
    )

    assert status.destination == tmp_path / ".agents" / "skills" / SKILL_NAME


def test_user_target_honors_codex_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))

    status = install_bundled_skill(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        target="user",
    )

    assert status.destination == tmp_path / "codex" / "skills" / SKILL_NAME


def test_output_overrides_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))

    status = install_bundled_skill(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        target="user",
        output=tmp_path / "custom",
    )

    assert status.target == "output"
    assert status.destination == tmp_path / "custom" / SKILL_NAME


def test_missing_bundled_skill_raises() -> None:
    with pytest.raises(SkillNotFound):
        skill_status(
            package=PACKAGE,
            distribution=DIST,
            resource_root=RESOURCE_ROOT,
            skill_name="missing",
            output="unused",
        )


@pytest.mark.parametrize(
    ("skill_name", "message"),
    [
        ("missing-skill-file", "缺少 SKILL.md"),
        ("missing-frontmatter", "缺少 frontmatter"),
        ("missing-description", "name 和 description"),
        ("wrong-name", "不一致"),
    ],
)
def test_invalid_bundled_skill_raises(skill_name: str, message: str) -> None:
    with pytest.raises(InvalidBundledSkill, match=message):
        skill_status(
            package=PACKAGE,
            distribution=DIST,
            resource_root=RESOURCE_ROOT,
            skill_name=skill_name,
            output="unused",
        )


def test_status_detects_outdated_versions(tmp_path: Path) -> None:
    destination = tmp_path / SKILL_NAME
    destination.mkdir()
    (destination / INSTALL_METADATA_FILE).write_text(
        json.dumps({"package_version": "1.2.2"}), encoding="utf-8"
    )

    status = skill_status(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        output=tmp_path,
    )

    assert status.installed is True
    assert status.installed_version == "1.2.2"
    assert status.outdated is True


def test_status_treats_missing_metadata_as_outdated(tmp_path: Path) -> None:
    (tmp_path / SKILL_NAME).mkdir()

    status = skill_status(
        package=PACKAGE,
        distribution=DIST,
        resource_root=RESOURCE_ROOT,
        skill_name=SKILL_NAME,
        output=tmp_path,
    )

    assert status.installed is True
    assert status.installed_version is None
    assert status.outdated is True
