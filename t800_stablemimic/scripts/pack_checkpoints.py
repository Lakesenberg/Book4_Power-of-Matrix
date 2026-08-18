"""Pack Windows tracking checkpoints for Linux StableMimic / get-up resume."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_latest_ckpt import describe, latest_model, pick_run

MUST_PARAM_FILES = ("env.yaml", "agent.yaml", "env.pkl", "agent.pkl")


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def pack(
    lab_root: Path,
    out_dir: Path,
    experiment: str = "tracking_t800",
    load_run: str | None = None,
    stage: str = "WIN1_TRACKING",
) -> dict:
    log_root = lab_root / "logs" / "rsl_rl" / experiment
    run_dir = pick_run(log_root, load_run)
    if run_dir is None:
        raise FileNotFoundError(f"找不到训练 run: {log_root}")
    ckpt = latest_model(run_dir)
    if ckpt is None:
        raise FileNotFoundError(f"找不到 checkpoint: {run_dir}/model_*.pt")

    dest_run = out_dir / "logs" / "rsl_rl" / experiment / run_dir.name
    dest_run.mkdir(parents=True, exist_ok=True)
    copy_file(ckpt, dest_run / ckpt.name)

    missing_params = []
    for name in MUST_PARAM_FILES:
        src = run_dir / "params" / name
        if src.is_file():
            copy_file(src, dest_run / "params" / name)
        else:
            missing_params.append(name)

    motion_copied = []
    for rel in (
        Path("datasets/tracking/t800/dance_t800.npz"),
        Path("datasets/tracking/t800/dance_t800.csv"),
    ):
        src = lab_root / rel
        if src.is_file():
            copy_file(src, out_dir / rel)
            motion_copied.append(str(rel))

    info = describe(run_dir, ckpt)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stage_completed": stage,
        "next_linux_stage": "LIN1_RESUME_OR_SCALE",
        "task": "Tracking-Flat-T800-Wo-State-Estimation-v0",
        "experiment_name": experiment,
        "run_name": info["run_name"],
        "checkpoint_name": info["checkpoint_name"],
        "iteration": info["iteration"],
        "source_run_dir": info["run_dir"],
        "packed_checkpoint": str(Path("logs/rsl_rl") / experiment / run_dir.name / ckpt.name),
        "motion_files": motion_copied,
        "missing_params": missing_params,
        "linux_resume_cmd": (
            "python scripts/tracking/train.py "
            "--task Tracking-Flat-T800-Wo-State-Estimation-v0 "
            "--headless --num_envs 4096 "
            "--motion_file datasets/tracking/t800/dance_t800.npz "
            "--resume True "
            f"--load_run {info['run_name']} "
            f"--checkpoint {info['checkpoint_name']}"
        ),
        "do_not_copy": [
            "videos/",
            "wandb/",
            "logs/rsl_rl/temp/",
            "Isaac Sim / Isaac Lab 安装目录",
        ],
        "notes": [
            "obs/action 与官方 T800 tracking 一致，Linux 可直接 runner.load(model_*.pt)",
            "StableMimic Lite / MoE 用该 pt 做初始化，不要换观测顺序",
            "get-up / 扭曲课程在 Linux 做，Windows 包里不必有 getup npz",
        ],
    }
    manifest_path = out_dir / "handoff" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    readme = out_dir / "HANDOFF_README.txt"
    readme.write_text(
        "\n".join(
            [
                "把本目录整个拷到 Linux 上的 engineai_rl_lab 根目录合并。",
                f"已完成阶段: {stage}",
                f"checkpoint: {manifest['packed_checkpoint']}",
                f"iteration: {manifest['iteration']}",
                "",
                "Linux 续训 tracking（升并行）:",
                manifest["linux_resume_cmd"],
                "",
                "然后用同一 model_*.pt 初始化 StableMimic Lite / 扭曲起身。",
                "详见 t800_stablemimic/CHECKPOINT_HANDOFF.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--experiment", default="tracking_t800")
    parser.add_argument("--load-run", default=None)
    parser.add_argument("--stage", default="WIN1_TRACKING")
    args = parser.parse_args()

    try:
        manifest = pack(args.lab_root, args.out_dir, args.experiment, args.load_run, args.stage)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 1

    print("[OK] 已打包到", args.out_dir)
    print("     run:        ", manifest["run_name"])
    print("     checkpoint: ", manifest["checkpoint_name"])
    print("     iteration:  ", manifest["iteration"])
    print("     manifest:   ", args.out_dir / "handoff" / "manifest.json")
    if manifest["missing_params"]:
        print("[WARN] 缺少 params:", ", ".join(manifest["missing_params"]))
    if not manifest["motion_files"]:
        print("[WARN] 未找到 dance_t800.npz/csv，Linux 上请自行放入 datasets/tracking/t800/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
