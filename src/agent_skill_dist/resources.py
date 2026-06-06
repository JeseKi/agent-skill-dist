from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from agent_skill_dist.exceptions import InvalidBundledSkill, SkillNotFound


def get_bundled_skill(package: str, resource_root: str, skill_name: str) -> Traversable:
    try:
        root = resources.files(package)
    except ModuleNotFoundError as exc:
        raise SkillNotFound(f"无法导入 package：{package!r}") from exc

    skill = root.joinpath(resource_root, skill_name)
    if not skill.is_dir():
        raise SkillNotFound(
            f"在 {package}:{resource_root} 下找不到内置 skill：{skill_name!r}"
        )
    return skill


def validate_bundled_skill(skill: Traversable, skill_name: str) -> None:
    skill_file = skill.joinpath("SKILL.md")
    if not skill_file.is_file():
        raise InvalidBundledSkill(f"内置 skill {skill_name!r} 缺少 SKILL.md")

    frontmatter = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not name or not description:
        raise InvalidBundledSkill(
            f"内置 skill {skill_name!r} 必须在 frontmatter 中定义 name 和 description"
        )
    if name != skill_name:
        raise InvalidBundledSkill(
            f"内置 skill 的 frontmatter name {name!r} 与 {skill_name!r} 不一致"
        )


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise InvalidBundledSkill("SKILL.md 缺少 frontmatter")

    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            continue
        data[key.strip()] = _strip_yaml_scalar(value.strip())

    raise InvalidBundledSkill("SKILL.md frontmatter 未闭合")


def _strip_yaml_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def copy_traversable_tree(source: Traversable, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        child_destination = destination / child.name
        if child.is_dir():
            copy_traversable_tree(child, child_destination)
        elif child.is_file():
            child_destination.write_bytes(child.read_bytes())
