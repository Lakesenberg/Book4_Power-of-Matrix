#!/usr/bin/env bash
# 在 WSL 里安装 Isaac Sim 5.1 + Isaac Lab 2.3.2。
# 需要: WSL2、Windows NVIDIA 驱动、nvidia-smi 能看到 GPU。
set -euo pipefail

apt_get() {
  sudo apt-get \
    -o Acquire::Check-Date=false \
    -o Acquire::Check-Valid-Until=false \
    "$@"
}

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "[错误] WSL 里没有 nvidia-smi。先更新 Windows 上的 NVIDIA 驱动并重启。"
  exit 1
fi
nvidia-smi -L

# WSL 时钟经常慢，hwclock 可能不存在；apt 一律跳过 Release 日期
apt_get update
apt_get install -y git wget build-essential cmake curl ca-certificates

ISAACLAB_DIR="${ISAACLAB_DIR:-$HOME/IsaacLab}"
VENV="${ISAAC_VENV:-$HOME/env_isaaclab}"
PINNED_COMMIT="c22775241e28f465fe345fa1a482ad6d29d712b0"
PY=""

if command -v python3.11 >/dev/null 2>&1; then
  PY=python3.11
elif apt_get install -y python3.11 python3.11-venv python3.11-dev; then
  PY=python3.11
fi

if [[ -z "$PY" ]]; then
  echo "[INFO] 当前 Ubuntu 没有 python3.11 包（Resolute 常见）。改用 conda 建 3.11 环境。"
  if ! command -v conda >/dev/null 2>&1; then
    echo "[错误] 请先: conda create -n isaaclab python=3.11 -y && conda activate isaaclab"
    echo "然后重新运行本脚本。"
    exit 1
  fi
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate base
  conda create -y -n isaaclab python=3.11
  conda activate isaaclab
  PY=python
else
  if [[ ! -x "$VENV/bin/python" ]]; then
    "$PY" -m venv "$VENV"
  fi
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
fi

python -m pip install -U pip
export PIP_DEFAULT_TIMEOUT=180
export PIP_RETRIES=10

echo "[INFO] 安装 Isaac Sim 5.1（很大，请保持网络稳定）"
echo "[INFO] 若出现 Connection interrupted / SSL EOF，先等 pip 自己续传，不要 Ctrl+C"
pip install --retries 10 --timeout 180 \
  "isaacsim[all,extscache]==5.1.0" \
  --extra-index-url https://pypi.nvidia.com

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

echo "[OK] Python: $(command -v python)  $(python --version)"
echo "下一步: bash $KIT/wsl/03_convert_and_train.sh"
echo "若用的是 conda isaaclab: 先 conda activate isaaclab"
echo "若用的是 venv: source $VENV/bin/activate"
