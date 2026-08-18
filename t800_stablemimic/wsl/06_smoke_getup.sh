#!/usr/bin/env bash
# 只跑很少环境和迭代，用来确认能出现 Learning iteration，不要用来出策略。
set -euo pipefail
export NUM_ENVS="${NUM_ENVS:-16}"
export MAX_ITERS="${MAX_ITERS:-3}"
export RUN_NAME="${RUN_NAME:-smoke_getup}"
exec "$(dirname "$0")/04_train_getup.sh"
