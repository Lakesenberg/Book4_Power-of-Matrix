#!/usr/bin/env bash
# 兼容旧名字。现在的主线是静态扭曲起身，不是舞中被推倒。
set -euo pipefail
echo "[INFO] StableMimic Lite（舞中推倒）已不是默认路径。"
echo "      静态扭曲起身请跑: $(dirname "$0")/04_train_getup.sh"
echo "      说明: t800_stablemimic/getup/README.md"
exec "$(dirname "$0")/04_train_getup.sh"
