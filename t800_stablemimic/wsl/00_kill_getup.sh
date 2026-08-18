#!/usr/bin/env bash
# 停掉所有起身训练，避免多个 Isaac 抢 PhysX。
set -euo pipefail
pkill -9 -f 'scripts/getup/train.py' || true
pkill -9 -f '04_train_getup.sh' || true
pkill -9 -f '06_smoke_getup.sh' || true
sleep 2
if pgrep -af 'scripts/getup/train.py' >/dev/null; then
  echo "[WARN] 仍有 getup 进程："
  pgrep -af 'scripts/getup/train.py'
  exit 1
fi
echo "已停干净"
