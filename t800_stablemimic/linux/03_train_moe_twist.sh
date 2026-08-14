#!/usr/bin/env bash
# Linux: MoE + 扭曲姿势课程。必须先有 LIN2 的 checkpoint。
set -euo pipefail
LAB_ROOT="${ENGINEAI_RL_LAB:-$PWD}"
cd "$LAB_ROOT"

if [[ -z "${LOAD_RUN:-}" || -z "${CHECKPOINT:-}" ]]; then
  echo "用法: LOAD_RUN=<lin2_run> CHECKPOINT=model_XXXX.pt $0"
  echo "LOAD_RUN 是 logs/rsl_rl/tracking_t800/ 下 LIN2 的文件夹名"
  exit 1
fi

python scripts/tracking/train.py \
  --task "${TASK:-Tracking-StableMimic-T800-v0}" \
  --headless \
  --num_envs "${NUM_ENVS:-4096}" \
  --motion_file datasets/tracking/t800/dance_t800.npz \
  --resume True \
  --load_run "$LOAD_RUN" \
  --checkpoint "$CHECKPOINT" \
  --run_name lin3_moe_twist
