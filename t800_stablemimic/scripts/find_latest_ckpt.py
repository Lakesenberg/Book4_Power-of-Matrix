"""Locate the newest RSL-RL run and checkpoint under engineai_rl_lab/logs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MODEL_RE = re.compile(r"^model_(\d+)\.pt$")


def iter_runs(log_root: Path) -> list[Path]:
    if not log_root.is_dir():
        return []
    return [p for p in log_root.iterdir() if p.is_dir() and (p / "params").is_dir()]


def latest_model(run_dir: Path) -> Path | None:
    models = []
    for p in run_dir.glob("model_*.pt"):
        m = MODEL_RE.match(p.name)
        if m:
            models.append((int(m.group(1)), p))
    if not models:
        # official play example also uses dance.pt
        dance = run_dir / "dance.pt"
        return dance if dance.is_file() else None
    models.sort(key=lambda x: x[0])
    return models[-1][1]


def pick_run(log_root: Path, load_run: str | None = None) -> Path | None:
    if load_run:
        candidate = log_root / load_run
        return candidate if candidate.is_dir() else None
    runs = iter_runs(log_root)
    if not runs:
        return None
    runs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return runs[0]


def describe(run_dir: Path, ckpt: Path) -> dict:
    iteration = None
    m = MODEL_RE.match(ckpt.name)
    if m:
        iteration = int(m.group(1))
    return {
        "run_dir": str(run_dir),
        "run_name": run_dir.name,
        "checkpoint": str(ckpt),
        "checkpoint_name": ckpt.name,
        "iteration": iteration,
        "params_dir": str(run_dir / "params"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", type=Path, required=True, help="engineai_rl_lab root")
    parser.add_argument("--experiment", default="tracking_t800")
    parser.add_argument("--load-run", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    log_root = args.lab_root / "logs" / "rsl_rl" / args.experiment
    run_dir = pick_run(log_root, args.load_run)
    if run_dir is None:
        print(f"[ERROR] 没有找到 run: {log_root}")
        return 1
    ckpt = latest_model(run_dir)
    if ckpt is None:
        print(f"[ERROR] run 里没有 model_*.pt: {run_dir}")
        return 1
    info = describe(run_dir, ckpt)
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print(f"run:        {info['run_name']}")
        print(f"checkpoint: {info['checkpoint']}")
        print(f"iteration:  {info['iteration']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
