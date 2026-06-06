from __future__ import annotations

import json

from agent_skill_dist.exceptions import SkillAlreadyExists
from agent_skill_dist.types import SkillInstallStatus


def status_to_text(status: SkillInstallStatus) -> str:
    """为父 CLI 格式化安装状态输出。"""

    installed = "是" if status.installed else "否"
    outdated = "是" if status.outdated else "否"
    unknown = "未知"
    lines = [
        f"skill：{status.skill_name}",
        f"目标：{status.target}",
        f"安装路径：{status.destination}",
        f"已安装：{installed}",
        f"内置版本：{status.bundled_version or unknown}",
        f"已安装版本：{status.installed_version or unknown}",
        f"已过期：{outdated}",
    ]
    return "\n".join(lines)


def install_to_text(status: SkillInstallStatus) -> str:
    """为父 CLI 格式化安装成功输出。"""

    version = status.bundled_version or "未知"
    return f"已安装 {status.skill_name} 到 {status.destination}\n版本：{version}"


def already_exists_to_text(exc: SkillAlreadyExists) -> str:
    """为已存在异常格式化可操作提示。"""

    return f"目标 skill 已存在：{exc.destination}\n如需覆盖，请加 --yes。"


def status_to_json(status: SkillInstallStatus) -> str:
    """为支持结构化输出的 CLI 返回紧凑 JSON。"""

    return json.dumps(status.to_dict(), sort_keys=True)
