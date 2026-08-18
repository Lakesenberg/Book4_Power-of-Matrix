#!/usr/bin/env bash
# 静态扭曲起身：不转舞蹈、不推倒。先把任务打进 vendor lab 再训。
set -euo pipefail

VENV="${ISAAC_VENV:-$HOME/env_isaaclab}"
KIT="$HOME/Book4_Power-of-Matrix/t800_stablemimic"
LAB="$KIT/vendor/engineai_rl_lab"
NUM_ENVS="${NUM_ENVS:-32}"

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

if pgrep -f 'scripts/.*/train.py' >/dev/null; then
  echo "[INFO] 发现旧的 train.py，先停掉，避免两个 Isaac 抢 PhysX"
  pkill -9 -f 'scripts/getup/train.py' || true
  pkill -9 -f 'scripts/tracking/train.py' || true
  sleep 3
fi
if pgrep -f 'scripts/.*/train.py' >/dev/null; then
  echo "[错误] 仍有训练进程，先: bash $KIT/wsl/00_kill_getup.sh"
  pgrep -af 'scripts/.*/train.py'
  exit 1
fi

python "$KIT/getup/apply_getup_overlay.py" --lab-root "$LAB"
python "$KIT/wsl/patch_usd_abspath.py" --lab-root "$LAB"
if head -n 1 "$LAB/source/engineai_rl_lab/engineai_rl_lab/assets/t800/serial_t800.usd" 2>/dev/null | grep -q git-lfs; then
  echo "[INFO] USD 还是 LFS 指针，先拉取真文件"
  bash "$KIT/wsl/fetch_usd_lfs.sh" "$LAB"
fi

cd "$LAB"
echo "[INFO] 开始静态扭曲起身: Getup-Twisted-T800-v0"
echo "      num_envs=$NUM_ENVS  （先 32 冒烟；出现 Learning iteration 再加）"
echo "      不使用 dance_t800.npz，不从 tracking 热启动（观测不同）"
python scripts/getup/train.py \
  --task Getup-Twisted-T800-v0 \
  --headless \
  --num_envs "$NUM_ENVS" \
  --device cuda:0 \
  --max_iterations "${MAX_ITERS:-15000}" \
  --run_name "${RUN_NAME:-wsl1_getup}"

echo "[OK] 日志: $LAB/logs/rsl_rl/getup_t800/"
echo "回放: bash $KIT/wsl/05_play_getup.sh"
