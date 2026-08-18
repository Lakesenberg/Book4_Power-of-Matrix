#!/usr/bin/env bash
# WSL 里转换动作并开始 T800 tracking（headless）。
set -euo pipefail

VENV="${ISAAC_VENV:-$HOME/env_isaaclab}"
KIT="$HOME/Book4_Power-of-Matrix/t800_stablemimic"
LAB="$KIT/vendor/engineai_rl_lab"
NUM_ENVS="${NUM_ENVS:-2048}"

activate_isaac() {
  if [[ -n "${CONDA_PREFIX:-}" && "$(basename "$CONDA_PREFIX")" == "isaaclab" ]]; then
    echo "[INFO] 已在 conda isaaclab: $CONDA_PREFIX"
    return 0
  fi
  if [[ -x "$VENV/bin/python" ]]; then
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
    return 0
  fi
  if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate isaaclab
    return 0
  fi
  echo "[错误] 找不到 Isaac 环境。先: conda activate isaaclab"
  exit 1
}

activate_isaac
echo "[INFO] Python: $(command -v python)  $(python --version)"

python "$KIT/wsl/patch_usd_abspath.py" --lab-root "$LAB"
python -c "import wandb" 2>/dev/null || python -m pip install -U wandb
if head -n 1 "$LAB/source/engineai_rl_lab/engineai_rl_lab/assets/t800/serial_t800.usd" 2>/dev/null | grep -q git-lfs; then
  echo "[INFO] USD 还是 LFS 指针，先拉取真文件"
  bash "$KIT/wsl/fetch_usd_lfs.sh" "$LAB"
fi

if [[ ! -f "$LAB/datasets/tracking/t800/dance_t800.csv" ]]; then
  echo "[错误] 找不到 dance_t800.csv，先跑 01_clone.sh"
  exit 1
fi

cd "$LAB"
echo "[INFO] csv → npz"
python scripts/csv_to_npz.py --robot t800 --input_fps 30 --headless \
  -f datasets/tracking/t800/dance_t800.csv
if [[ ! -f "$LAB/datasets/tracking/t800/dance_t800.npz" ]]; then
  echo "[错误] 未生成 dance_t800.npz，不要继续训练。先跑: bash $KIT/wsl/fix_runtime.sh"
  exit 1
fi

echo "[INFO] 开始 tracking: Tracking-Flat-T800-Wo-State-Estimation-v0"
echo "      num_envs=$NUM_ENVS  （显存不够: NUM_ENVS=1024 bash $0）"
python scripts/tracking/train.py \
  --task Tracking-Flat-T800-Wo-State-Estimation-v0 \
  --headless \
  --num_envs "$NUM_ENVS" \
  --device cuda:0 \
  --max_iterations 20000 \
  --run_name wsl1_tracking \
  --motion_file datasets/tracking/t800/dance_t800.npz

echo "[OK] 日志: $LAB/logs/rsl_rl/tracking_t800/"
echo "打包: python $KIT/scripts/pack_checkpoints.py --lab-root $LAB --out-dir $KIT/handoff_windows_to_linux --stage WIN1_TRACKING"
