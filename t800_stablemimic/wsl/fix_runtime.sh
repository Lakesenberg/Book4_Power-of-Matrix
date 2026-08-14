#!/usr/bin/env bash
# 补 WSL 运行时库、wandb，并把 T800 USD 改成绝对路径。
set -euo pipefail

KIT="$HOME/Book4_Power-of-Matrix/t800_stablemimic"
LAB="$KIT/vendor/engineai_rl_lab"

sudo apt-get -o Acquire::Check-Date=false -o Acquire::Check-Valid-Until=false update
sudo apt-get -o Acquire::Check-Date=false -o Acquire::Check-Valid-Until=false install -y \
  libxt6 libglu1-mesa libx11-6 libxext6 libgl1 libxi6 libxrandr2 libxinerama1 libxcursor1

if command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate isaaclab
fi
python -m pip install -U wandb

python "$KIT/wsl/patch_usd_abspath.py" --lab-root "$LAB"

USD="$LAB/source/engineai_rl_lab/engineai_rl_lab/assets/t800/serial_t800.usd"
if [[ ! -f "$USD" ]]; then
  echo "[错误] 找不到 $USD"
  echo "在 lab 目录执行: git lfs install && git lfs pull"
  exit 1
fi
echo "[OK] USD: $USD"
echo "[OK] 运行时已补齐。下一步:"
echo "  conda activate isaaclab"
echo "  bash $KIT/wsl/03_convert_and_train.sh"
