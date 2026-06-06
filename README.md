# agent-skill-dist

`agent-skill-dist` 是一个很小的 Python 库，面向需要随 wheel 分发
canonical agent skill 的 CLI 包。它让 CLI 包可以把内置 skill 显式安装到
agent 已扫描的 skill 目录中。

MVP 对齐 Codex 风格的 skill 目录：

- repo 安装：`./.agents/skills/<skill-name>`
- user 安装：`${CODEX_HOME:-~/.codex}/skills/<skill-name>`
- 自定义安装：`<output>/<skill-name>`

安装必须显式触发。除非父 CLI 传入 `yes=True`，否则已有 skill 不会被替换。

## 包内目录结构

消费方 package 可以按下面的结构内置 skill：

```text
my_cli/
  bundled_skills/
    my-cli/
      SKILL.md
      references/command-guide.md
```

`SKILL.md` 必须包含带有 `name` 和 `description` 的 frontmatter，并且
frontmatter 中的 `name` 必须和 skill 目录名一致。

```markdown
---
name: my-cli
description: 让 agent 安全操作 My CLI 工具。
---

# My CLI
```

## API

```python
from agent_skill_dist import install_bundled_skill, skill_status

status = skill_status(
    package="my_cli",
    distribution="my-cli",
    resource_root="bundled_skills",
    skill_name="my-cli",
    target="user",
)

install_bundled_skill(
    package="my_cli",
    distribution="my-cli",
    resource_root="bundled_skills",
    skill_name="my-cli",
    package_version="1.3.1",
    target="repo",
    yes=False,
)
```

两个函数都会返回 `SkillInstallStatus` dataclass：

```python
{
    "skill_name": "my-cli",
    "target": "user",
    "destination": "/home/me/.codex/skills/my-cli",
    "bundled_version": "1.3.1",
    "installed_version": "1.3.0",
    "installed": True,
    "outdated": True,
    "would_overwrite": True,
    "metadata_path": "/home/me/.codex/skills/my-cli/.agent-skill-install.json",
}
```

`package_version` 是可选参数。传入时会优先用于 `bundled_version`、状态判断和
`.agent-skill-install.json`；不传时 fallback 到
`importlib.metadata.version(distribution)`。

## CLI 集成

本库不依赖 Typer、Click 或 argparse。父 CLI 可以把 API 接入自己的命令框架：

```bash
mycli skill status
mycli skill install --target repo
mycli skill install --target user --yes
mycli skill install --target global --yes
mycli skill install --output .agents/skills --yes
```

`target="global"` 是 `target="user"` 的 alias，安装路径仍然是
`${CODEX_HOME:-~/.codex}/skills/<skill-name>`。

如果需要人类可读输出或 JSON 输出 helper：

```python
from agent_skill_dist.cli import (
    already_exists_to_text,
    install_to_text,
    status_to_json,
    status_to_text,
)
```

`SkillAlreadyExists` 暴露 `destination` 字段，父 CLI 可以用
`already_exists_to_text()` 输出覆盖提示。

## Hatchling 包数据

使用 Hatchling 的消费方可以这样把内置 skill 文件打进 wheel：

```toml
[tool.hatch.build.targets.wheel]
packages = ["my_cli"]
artifacts = [
  "my_cli/bundled_skills/**",
]
```

## 开发

```bash
uv run pytest
uv build
```

本包包含 `py.typed`，类型检查器可以直接使用源码中的类型标注。
