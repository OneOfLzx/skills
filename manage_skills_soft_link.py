#!/usr/bin/env python3
"""管理当前 skills 目录到 ~/.claude/skills 的软连接。

直接运行脚本会显示交互菜单，也可以使用命令行参数：

    python manage_claude_skills_link.py enable
    python manage_claude_skills_link.py disable
    python manage_claude_skills_link.py status

Windows 创建目录软连接可能需要开发者模式或管理员权限。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


SOURCE = Path(__file__).resolve().parent
TARGET = Path.home() / ".claude" / "skills"


def is_link_to_source(path: Path) -> bool:
    """判断 path 是否是指向 SOURCE 的软连接（兼容 Windows junction）。"""
    if not path.is_symlink():
        return False
    try:
        return path.resolve(strict=False) == SOURCE
    except OSError:
        return False


def show_status() -> None:
    if is_link_to_source(TARGET):
        print(f"状态：已开启\n  {TARGET} -> {SOURCE}")
    elif TARGET.is_symlink():
        print(f"状态：目标是指向其他位置的软连接\n  {TARGET} -> {TARGET.resolve(strict=False)}")
    elif TARGET.exists():
        print(f"状态：未开启（目标已存在且不是软连接）\n  {TARGET}")
    else:
        print(f"状态：未开启\n  目标不存在：{TARGET}")


def enable_link() -> int:
    if is_link_to_source(TARGET):
        print(f"软连接已经开启：{TARGET} -> {SOURCE}")
        return 0

    if TARGET.exists() or TARGET.is_symlink():
        print(
            f"无法开启：目标已存在且不是指向当前目录的软连接：\n  {TARGET}\n"
            "为避免覆盖现有文件，脚本不会自动删除或移动它。"
        )
        return 1

    try:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        # target_is_directory 仅 Windows 需要；其他平台会忽略该参数。
        os.symlink(SOURCE, TARGET, target_is_directory=True)
    except (OSError, NotImplementedError) as error:
        print(f"创建软连接失败：{error}")
        if sys.platform.startswith("win"):
            print("Windows 提示：请开启开发者模式，或使用管理员权限运行。")
        return 1

    print(f"软连接已开启：{TARGET} -> {SOURCE}")
    return 0


def disable_link() -> int:
    if not TARGET.is_symlink():
        if TARGET.exists():
            print(f"未关闭：{TARGET} 是真实目录/文件，脚本不会删除它。")
        else:
            print("软连接本来就未开启。")
        return 0

    if not is_link_to_source(TARGET):
        print(f"未关闭：{TARGET} 指向其他位置，脚本不会删除它。")
        return 1

    try:
        # unlink 只删除链接本身，不会删除 SOURCE 目录内容。
        TARGET.unlink()
    except OSError as error:
        print(f"关闭软连接失败：{error}")
        return 1

    print(f"软连接已关闭：{TARGET}")
    return 0


def interactive_menu() -> int:
    print("\nClaude skills 软连接管理")
    print("1. 开启软连接")
    print("2. 关闭软连接")
    print("3. 查看状态")
    print("0. 退出")
    choice = input("请选择 [1/2/3/0]：").strip()

    if choice == "1":
        return enable_link()
    if choice == "2":
        return disable_link()
    if choice == "3":
        show_status()
        return 0
    if choice == "0":
        return 0

    print("无效选项，脚本退出。")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="管理 ~/.claude/skills 软连接")
    parser.add_argument("action", nargs="?", choices=("enable", "disable", "status"))
    args = parser.parse_args()

    if args.action == "enable":
        return enable_link()
    if args.action == "disable":
        return disable_link()
    if args.action == "status":
        show_status()
        return 0
    return interactive_menu()


if __name__ == "__main__":
    raise SystemExit(main())
