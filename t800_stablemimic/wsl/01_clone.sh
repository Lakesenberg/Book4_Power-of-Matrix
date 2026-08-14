#!/usr/bin/env bash
# 在 WSL Ubuntu 里运行。必须已在家目录，不要在 /mnt/c/Windows/System32。
set -euo pipefail

if [[ "$(pwd)" == /mnt/c/Windows/System32* ]] || [[ "$(pwd)" == /mnt/c/windows/system32* ]]; then
  echo "[错误] 你还在 Windows System32 的挂载点。先执行: cd ~"
  exit 1
fi

cd "$HOME"
if [[ ! -d "$HOME/Book4_Power-of-Matrix/.git" ]]; then
  git clone -b cursor/t800-windows-train-2191 \
    https://github.com/Lakesenberg/Book4_Power-of-Matrix.git \
    "$HOME/Book4_Power-of-Matrix"
else
  git -C "$HOME/Book4_Power-of-Matrix" fetch origin
  git -C "$HOME/Book4_Power-of-Matrix" checkout cursor/t800-windows-train-2191
  git -C "$HOME/Book4_Power-of-Matrix" pull --ff-only origin cursor/t800-windows-train-2191 || true
fi

KIT="$HOME/Book4_Power-of-Matrix/t800_stablemimic"
LAB="$KIT/vendor/engineai_rl_lab"
mkdir -p "$KIT/vendor"
if [[ ! -f "$LAB/scripts/tracking/train.py" ]]; then
  git clone --depth 1 https://github.com/engineai-robotics/engineai_rl_lab.git "$LAB"
fi

echo "[OK] 仓库: $KIT"
echo "[OK] 官方 lab: $LAB"
echo "下一步: bash $KIT/wsl/02_install_isaaclab.sh"
