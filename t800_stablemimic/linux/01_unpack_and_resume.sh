#!/usr/bin/env bash
# 在 Linux 的 engineai_rl_lab 根目录执行。
# 用法: ./01_unpack_and_resume.sh /path/to/handoff_windows_to_linux
set -euo pipefail

HANDOFF="${1:?用法: $0 /path/to/handoff_windows_to_linux}"
LAB_ROOT="${ENGINEAI_RL_LAB:-$PWD}"
MANIFEST="$HANDOFF/handoff/manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "[ERROR] 找不到 $MANIFEST"
  exit 1
fi

python3 - <<'PY' "$HANDOFF" "$LAB_ROOT"
import json, shutil, sys
from pathlib import Path
handoff, lab = Path(sys.argv[1]), Path(sys.argv[2])
manifest = json.loads((handoff / "handoff" / "manifest.json").read_text())
src_ckpt = handoff / manifest["packed_checkpoint"]
dst_ckpt = lab / manifest["packed_checkpoint"]
dst_ckpt.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src_ckpt, dst_ckpt)
src_params = src_ckpt.parent / "params"
if src_params.is_dir():
    shutil.copytree(src_params, dst_ckpt.parent / "params", dirs_exist_ok=True)
for rel in ("datasets/tracking/t800/dance_t800.npz", "datasets/tracking/t800/dance_t800.csv"):
    src = handoff / rel
    if src.is_file():
        dst = lab / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
(lab / "handoff").mkdir(exist_ok=True)
shutil.copy2(handoff / "handoff" / "manifest.json", lab / "handoff" / "manifest.json")
print("[OK] 已合并到", lab)
print("     checkpoint:", dst_ckpt)
print("     run:       ", manifest["run_name"])
print("     iter:      ", manifest["iteration"])
PY

echo
echo "升到 4096 并行续训 tracking（可选）:"
python3 - <<'PY' "$MANIFEST"
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["linux_resume_cmd"])
PY
