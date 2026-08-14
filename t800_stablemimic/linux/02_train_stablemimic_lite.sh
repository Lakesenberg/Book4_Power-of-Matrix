#!/usr/bin/env bash
# Linux: 用 Windows 的 tracking checkpoint 初始化，再上 get-up 支撑。
# 当前官方 engineai_rl_lab 还没有 get-up 任务；此脚本先把「必须带着的 pt」对齐好，
# 等 Tracking-StableMimic-T800-v0 合入后再把 TASK 改掉。
set -euo pipefail

LAB_ROOT="${ENGINEAI_RL_LAB:-$PWD}"
MANIFEST="${LAB_ROOT}/handoff/manifest.json"
if [[ ! -f "$MANIFEST" ]]; then
  echo "[ERROR] 先运行 01_unpack_and_resume.sh"
  exit 1
fi

RUN=$(python3 -c "import json; print(json.load(open('$MANIFEST'))['run_name'])")
CKPT=$(python3 -c "import json; print(json.load(open('$MANIFEST'))['checkpoint_name'])")
GETUP="${GETUP_FILE:-datasets/tracking/t800/getup/getup_lib.npz}"

echo "[INFO] 从 Windows tracking 初始化: run=$RUN ckpt=$CKPT"
echo "[INFO] get-up 库: $GETUP"
if [[ ! -f "$LAB_ROOT/$GETUP" ]]; then
  echo "[WARN] 还没有 get-up npz。请先用 csv_to_npz.py --robot t800 转仰卧/俯卧/侧卧轨迹。"
  echo "       没有 get-up 库时，先跑 01 的 tracking 升并行，不要空跑本脚本。"
  exit 2
fi

cd "$LAB_ROOT"
python scripts/tracking/train.py \
  --task "${TASK:-Tracking-StableMimic-T800-v0}" \
  --headless \
  --num_envs "${NUM_ENVS:-4096}" \
  --motion_file datasets/tracking/t800/dance_t800.npz \
  --resume True \
  --load_run "$RUN" \
  --checkpoint "$CKPT" \
  --run_name lin2_stablemimic_lite
