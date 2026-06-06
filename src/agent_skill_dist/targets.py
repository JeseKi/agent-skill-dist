from __future__ import annotations

import os
from pathlib import Path

from agent_skill_dist.exceptions import SkillDistError


def resolve_destination(
    *,
    target: str,
    output: str | Path | None,
    skill_name: str,
) -> Path:
    if output is not None:
        return Path(output).expanduser().resolve() / skill_name

    if target == "repo":
        return Path.cwd().resolve() / ".agents" / "skills" / skill_name
    if target == "user":
        codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
        return codex_home.resolve() / "skills" / skill_name

    raise SkillDistError("target 必须是 'repo' 或 'user'")
