"""Validate a packed Windows→Linux handoff folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(handoff_root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = handoff_root / "handoff" / "manifest.json"
    if not manifest_path.is_file():
        return [f"缺少 {manifest_path}"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ckpt = handoff_root / manifest["packed_checkpoint"]
    if not ckpt.is_file():
        errors.append(f"缺少 checkpoint: {ckpt}")
    run_dir = ckpt.parent
    for name in ("env.yaml", "agent.yaml"):
        if not (run_dir / "params" / name).is_file():
            errors.append(f"缺少 params/{name}")
    npz = handoff_root / "datasets/tracking/t800/dance_t800.npz"
    if not npz.is_file():
        errors.append("缺少 datasets/tracking/t800/dance_t800.npz（Linux 续训 tracking 必需）")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff-root", type=Path, required=True)
    args = parser.parse_args()
    errors = validate(args.handoff_root)
    if errors:
        print("[FAIL] handoff 不完整:")
        for e in errors:
            print("  -", e)
        return 1
    print("[OK] handoff 可以拷到 Linux")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
