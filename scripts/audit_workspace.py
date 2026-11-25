#!/usr/bin/env python3
"""只读检查 C:\\code 临时文件与构建残留；绝不修改或删除文件。"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

# 根目录允许存在、且用途明确的非业务目录。
ROOT_REPO_DIRS = {"projects", "learning", "ai-docs", "reference"}
ALLOWED_ROOT_DIRS = {
    ".git", ".claude", ".vscode", "docs", "scripts", *ROOT_REPO_DIRS,
}
# 有明确用途、由用户选择保留的本机目录：仅说明，不作为待清理警告。
PRESERVED_ROOT_DIRS = {
    ".superpowers": "历史任务账本；保留 progress/brief/report，不再存放大体积试验夹具",
    "m5-verify": "历史验证副本；既有计划明确要求保护",
    ".claude": "Claude Code 本机权限配置",
    ".vscode": "本机编辑器配置；检查配置有效性后再决定是否清理",
    ".scratch": "临时探针目录；本次用户要求保留活跃项，清理时先逐项审查",
}
# 这些目录是已知临时工作区；报告但不删除。
KNOWN_TEMP_DIRS = {
    ".scratch", ".tmp", ".ftmerge1", ".plan-extract", ".plan-extract2",
    ".plan-extract3", ".t1-check", ".algo-plan-verify", ".dsh-acl-out",
}
SUSPICIOUS_SUFFIXES = {".log", ".tmp", ".bak", ".orig", ".rej", ".dump"}
SUSPICIOUS_PREFIXES = ("debug", "dbg", "probe", "scratch", "temp", "tmp", "test-copy")


def git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout.strip()
    except OSError as exc:
        return f"git 执行失败：{exc}"


def size_and_latest(path: Path) -> tuple[int, int, float]:
    total = files = 0
    latest = 0.0
    for base, dirs, names in os.walk(path, topdown=True, followlinks=False):
        dirs[:] = [d for d in dirs if d != ".git" and d != "node_modules"]
        for name in names:
            fp = Path(base) / name
            try:
                st = fp.stat(follow_symlinks=False)
            except OSError:
                continue
            if not fp.is_file():
                continue
            files += 1
            total += st.st_size
            latest = max(latest, st.st_mtime)
    return total, files, latest


def print_candidate(path: Path, label: str) -> None:
    size, files, latest = size_and_latest(path)
    latest_s = "未知" if not latest else __import__("datetime").datetime.fromtimestamp(latest).strftime("%Y-%m-%d %H:%M")
    rel = path.relative_to(ROOT)
    tracked = git("ls-files", "--", rel.as_posix())
    print(f"WARN {label}: {rel} | {size / (1024**2):.1f} MiB | {files} 文件 | 最新 {latest_s} | tracked={'是' if tracked else '否'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="聚合仓根目录（默认脚本所在仓根）")
    args = parser.parse_args()
    root = args.root.resolve()
    if root != ROOT:
        print(f"ERROR 仅允许审计脚本所在仓根：{ROOT}")
        return 2

    print(f"只读工作区审计：{ROOT}")
    print("注意：本脚本只报告，绝不创建、移动或删除任何文件。\n")

    problems = 0
    for item in sorted(ROOT.iterdir(), key=lambda p: p.name.lower()):
        if item.is_dir() and not item.is_symlink():
            name = item.name
            if name in PRESERVED_ROOT_DIRS:
                print(f"INFO 已登记保留目录：{name} | {PRESERVED_ROOT_DIRS[name]}")
            elif name in KNOWN_TEMP_DIRS:
                print_candidate(item, "根目录已知临时目录")
                problems += 1
            elif name not in ALLOWED_ROOT_DIRS:
                print_candidate(item, "根目录未登记目录")
                problems += 1
        elif item.is_file() and item.name not in {
            ".gitattributes", ".gitignore", ".gitmodules", "LICENSE",
            "README.md", "repos.yaml", "AGENTS.md",
        }:
            low = item.name.lower()
            if item.suffix.lower() in SUSPICIOUS_SUFFIXES or low.startswith(SUSPICIOUS_PREFIXES):
                print_candidate(item, "根目录可疑散文件")
                problems += 1

    # 只检查聚合仓自身的 Git 状态；绝不把子仓路径交给父仓 git status。
    # 因而不会遍历子仓文件树，也不会把合法的子仓 tracked 文件误判为垃圾。
    status = git("status", "--porcelain", "--untracked-files=all")
    for line in status.splitlines():
        if not line.startswith("?? "):
            continue
        rel = line[3:].strip().replace("\\", "/")
        if "/" in rel or rel in {"AGENTS.md", "scripts/audit_workspace.py"}:
            continue
        path = ROOT / rel
        if not path.is_file():
            continue
        low = path.name.lower()
        if path.suffix.lower() in SUSPICIOUS_SUFFIXES or low.startswith(SUSPICIOUS_PREFIXES):
            print_candidate(path, "根仓未跟踪可疑文件")
            problems += 1

    print("\n建议：逐项确认用途、是否唯一内容、Git 跟踪状态与修改时间后再处理；不要对报告直接运行广域删除命令。")
    print(f"审计结束：{problems} 项需人工查看。")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
