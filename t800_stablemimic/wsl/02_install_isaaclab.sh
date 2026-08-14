#!/usr/bin/env bash
# 在 WSL Ubuntu 22.04 里安装 Isaac Sim 5.1 + Isaac Lab 2.3.2（官方 Linux 路径）。
# 需要: WSL2、Windows 上已装支持 WSL 的 NVIDIA 驱动、本机 nvidia-smi 在 WSL 里能看到 GPU。
set -euo pipefail

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "[错误] WSL 里没有 nvidia-smi。先在 Windows 更新 NVIDIA Game Ready/Studio 驱动，重启后再开 Ubuntu。"
  echo "不要在 WSL 里装 Windows 版显卡驱动。"
  exit 1
fi
nvidia-smi -L

sudo apt-get update
sudo apt-get install -y git wget build-essential cmake python3.11 python3.11-venv python3.11-dev

ISAACLAB_DIR="${ISAACLAB_DIR:-$HOME/IsaacLab}"
VENV="${ISAAC_VENV:-$HOME/env_isaaclab}"
PINNED_COMMIT="c22775241e28f465fe345fa1a482ad6d29d712b0"

if [[ ! -x "$VENV/bin/python" ]]; then
  python3.11 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install -U pip

echo "[INFO] 安装 Isaac Sim 5.1 pip 包（体积大，需较长时间）"
pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com

if [[ ! -d "$ISAACLAB_DIR/.git" ]]; then
  git clone https://github.com/isaac-sim/IsaacLab.git "$ISAACLAB_DIR"
fi
git -C "$ISAACLAB_DIR" fetch --all
git -C "$ISAACLAB_DIR" checkout "$PINNED_COMMIT"

cd "$ISAACLAB_DIR"
./isaaclab.sh -i rsl_rl

KIT="$HOME/Book4_Power-of-Matrix/t800_stablemimic"
LAB="$KIT/vendor/engineai_rl_lab"
if [[ ! -f "$LAB/scripts/tracking/train.py" ]]; then
  echo "[错误] 先运行 wsl/01_clone.sh"
  exit 1
fi
pip install -e "$LAB/source/engineai_rl_lab"

echo "[OK] Isaac 环境: $VENV"
echo "激活: source $VENV/bin/activate"
echo "下一步: bash $KIT/wsl/03_convert_and_train.sh"
