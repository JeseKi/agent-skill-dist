from __future__ import annotations

from pathlib import Path


class SkillDistError(Exception):
    """agent-skill-dist 的基础异常。"""


class SkillAlreadyExists(SkillDistError):
    """目标 skill 目录已存在且未启用覆盖时抛出。"""

    def __init__(self, destination: Path) -> None:
        self.destination = destination
        super().__init__(f"目标 skill 已存在：{destination}")


class SkillNotFound(SkillDistError):
    """在 package resources 中找不到内置 skill 时抛出。"""


class InvalidBundledSkill(SkillDistError):
    """内置 skill 不满足必要结构时抛出。"""
