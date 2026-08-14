#!/usr/bin/env bash
# 把 engineai_rl_lab 里的 *.usd 从 Git LFS 拉成真正的模型文件。
set -euo pipefail

LAB="${1:-$HOME/Book4_Power-of-Matrix/t800_stablemimic/vendor/engineai_rl_lab}"
USD="$LAB/source/engineai_rl_lab/engineai_rl_lab/assets/t800/serial_t800.usd"

if [[ ! -d "$LAB/.git" ]]; then
  echo "[错误] 不是 git 仓库: $LAB"
  exit 1
fi

sudo apt-get -o Acquire::Check-Date=false -o Acquire::Check-Valid-Until=false install -y git-lfs
git -C "$LAB" lfs install --local
echo "[INFO] git lfs pull in $LAB"
git -C "$LAB" lfs pull

is_pointer() {
  local f="$1"
  [[ -f "$f" ]] && head -n 1 "$f" | grep -q "git-lfs.github.com"
}

if is_pointer "$USD"; then
  echo "[WARN] lfs pull 后仍是指针，改用 GitHub media 直链"
  ROOT="https://media.githubusercontent.com/media/engineai-robotics/engineai_rl_lab/main"
  while IFS= read -r -d '' f; do
    rel="${f#"$LAB"/}"
    echo "  download $rel"
    curl -fsSL -o "$f" "$ROOT/$rel"
  done < <(find "$LAB/source/engineai_rl_lab/engineai_rl_lab/assets" -name "*.usd" -print0)
fi

if [[ ! -f "$USD" ]] || is_pointer "$USD"; then
  echo "[错误] 仍不是有效 USD: $USD"
  echo "请检查: wc -c $USD && head -n 2 $USD"
  exit 1
fi

echo "[OK] USD 大小 $(wc -c < "$USD") 字节: $USD"
echo "下一步: conda activate isaaclab && bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/03_convert_and_train.sh"
