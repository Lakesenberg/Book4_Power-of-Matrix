#!/usr/bin/env bash
# Linux / 本机: 静态扭曲起身（不依赖舞蹈 npz）。
set -euo pipefail
LAB_ROOT="${ENGINEAI_RL_LAB:-$PWD}"
KIT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$KIT/getup/apply_getup_overlay.py" --lab-root "$LAB_ROOT"
cd "$LAB_ROOT"
python scripts/getup/train.py \
  --task Getup-Twisted-T800-v0 \
  --headless \
  --num_envs "${NUM_ENVS:-4096}" \
  --device cuda:0 \
  --max_iterations "${MAX_ITERS:-15000}" \
  --run_name "${RUN_NAME:-lin_getup}"
