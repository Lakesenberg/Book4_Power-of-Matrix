#!/usr/bin/env bash
# 用已经能训的官方 tracking、16 环境、2 轮，确认 PhysX 还能过 sim.reset()。
set -euo pipefail

VENV="${ISAAC_VENV:-$HOME/env_isaaclab}"
KIT="$HOME/Book4_Power-of-Matrix/t800_stablemimic"
LAB="$KIT/vendor/engineai_rl_lab"

if pgrep -f 'scripts/.*/train.py' >/dev/null; then
  echo "[错误] 还有 train.py 在跑。先: bash $KIT/wsl/00_kill_getup.sh"
  pgrep -af 'scripts/.*/train.py'
  exit 1
fi

if [[ -n "${CONDA_PREFIX:-}" && "$(basename "$CONDA_PREFIX")" == "isaaclab" ]]; then
  :
elif command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate isaaclab
elif [[ -x "$VENV/bin/python" ]]; then
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
else
  echo "[错误] 先: conda activate isaaclab"
  exit 1
fi

python "$KIT/wsl/patch_usd_abspath.py" --lab-root "$LAB"
cd "$LAB"
echo "[INFO] PhysX 冒烟: 官方 tracking，16 环境，2 轮"
python scripts/tracking/train.py \
  --task Tracking-Flat-T800-Wo-State-Estimation-v0 \
  --headless \
  --num_envs 16 \
  --device cuda:0 \
  --max_iterations 2 \
  --run_name physx_smoke \
  --motion_file datasets/tracking/t800/dance_t800.npz

echo "[OK] 若出现 Learning iteration，说明 PhysX 可用，再跑 06_smoke_getup.sh"
