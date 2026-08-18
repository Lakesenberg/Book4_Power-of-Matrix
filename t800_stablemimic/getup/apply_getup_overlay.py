"""Copy the get-up task into a local engineai_rl_lab checkout."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OVERLAY_TASKS = HERE / "overlay" / "tasks" / "getup"
OVERLAY_SCRIPTS = HERE / "overlay" / "scripts" / "getup"
POSES = HERE / "poses.py"


def apply(lab_root: Path) -> list[Path]:
    lab_root = lab_root.resolve()
    dest_task = lab_root / "source" / "engineai_rl_lab" / "engineai_rl_lab" / "tasks" / "getup"
    dest_scripts = lab_root / "scripts" / "getup"
    if not (lab_root / "source" / "engineai_rl_lab" / "engineai_rl_lab" / "tasks").is_dir():
        raise FileNotFoundError(f"不是 engineai_rl_lab 根目录: {lab_root}")
    if dest_task.exists():
        shutil.rmtree(dest_task)
    shutil.copytree(OVERLAY_TASKS, dest_task)
    shutil.copy2(POSES, dest_task / "poses.py")
    dest_scripts.mkdir(parents=True, exist_ok=True)
    for src in OVERLAY_SCRIPTS.glob("*.py"):
        shutil.copy2(src, dest_scripts / src.name)
    written = [dest_task, dest_scripts / "train.py", dest_scripts / "play.py", dest_task / "poses.py"]
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        written = apply(args.lab_root)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 1
    print("[OK] 已写入 Getup-Twisted-T800-v0")
    for path in written:
        print("    ", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
