#!/usr/bin/env bash
# 拉取 T800 全部 USD 层。根文件只有 1.4KB，网格在 configuration/serial_t800_base.usd（约 31MB）。
set -euo pipefail

LAB="${1:-$HOME/Book4_Power-of-Matrix/t800_stablemimic/vendor/engineai_rl_lab}"
ASSET="$LAB/source/engineai_rl_lab/engineai_rl_lab/assets/t800"
ROOT="https://media.githubusercontent.com/media/engineai-robotics/engineai_rl_lab/main/source/engineai_rl_lab/engineai_rl_lab/assets/t800"

is_pointer() {
  local f="$1"
  [[ -f "$f" ]] && head -c 80 "$f" | grep -q "git-lfs.github.com"
}

download() {
  local rel="$1"
  local dest="$ASSET/$rel"
  mkdir -p "$(dirname "$dest")"
  echo "[INFO] download $rel"
  curl -fL --retry 5 --retry-delay 2 -o "$dest" "$ROOT/$rel"
}

if [[ ! -d "$LAB/.git" ]]; then
  echo "[错误] 不是 git 仓库: $LAB"
  exit 1
fi

sudo apt-get -o Acquire::Check-Date=false -o Acquire::Check-Valid-Until=false install -y git-lfs curl
git -C "$LAB" lfs install --local
git -C "$LAB" lfs pull || true

# 无论 lfs 是否完整，都用 GitHub media 覆盖这 5 个文件
download "serial_t800.usd"
download "configuration/serial_t800_base.usd"
download "configuration/serial_t800_physics.usd"
download "configuration/serial_t800_robot.usd"
download "configuration/serial_t800_sensor.usd"

fail=0
for f in \
  "$ASSET/serial_t800.usd" \
  "$ASSET/configuration/serial_t800_base.usd" \
  "$ASSET/configuration/serial_t800_physics.usd" \
  "$ASSET/configuration/serial_t800_robot.usd" \
  "$ASSET/configuration/serial_t800_sensor.usd"
do
  sz=$(wc -c < "$f")
  if is_pointer "$f"; then
    echo "[错误] 仍是 LFS 指针: $f"
    fail=1
  else
    echo "[OK] $sz  $f"
  fi
done

base_sz=$(wc -c < "$ASSET/configuration/serial_t800_base.usd")
if [[ "$base_sz" -lt 1000000 ]]; then
  echo "[错误] serial_t800_base.usd 只有 $base_sz 字节，应约 31MB"
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "[OK] T800 USD 层已齐。下一步:"
echo "  conda activate isaaclab"
echo "  bash $HOME/Book4_Power-of-Matrix/t800_stablemimic/wsl/03_convert_and_train.sh"
