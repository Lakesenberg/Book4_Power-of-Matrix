#!/usr/bin/env bash
# 回放最新 get-up checkpoint。无窗口时: HEADLESS=1 bash 05_play_getup.sh
set -euo pipefail

VENV="${ISAAC_VENV:-$HOME/env_isaaclab}"
KIT="$HOME/Book4_Power-of-Matrix/t800_stablemimic"
LAB="$KIT/vendor/engineai_rl_lab"

if [[ -n "${CONDA_PREFIX:-}" && "$(basename "$CONDA_PREFIX")" == "isaaclab" ]]; then
  :
elif [[ -x "$VENV/bin/python" ]]; then
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
elif command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate isaaclab
else
  echo "[错误] 先: conda activate isaaclab"
  exit 1
fi

python "$KIT/getup/apply_getup_overlay.py" --lab-root "$LAB"
python "$KIT/wsl/patch_usd_abspath.py" --lab-root "$LAB"

if [[ -z "${LOAD_RUN:-}" || -z "${CHECKPOINT:-}" ]]; then
  mapfile -t CKPT_INFO < <(python "$KIT/scripts/find_latest_ckpt.py" --lab-root "$LAB" --experiment getup_t800 --json \
    | python -c "import json,sys; d=json.load(sys.stdin); print(d['run_name']); print(d['checkpoint_name'])")
  LOAD_RUN="${CKPT_INFO[0]}"
  CHECKPOINT="${CKPT_INFO[1]}"
fi

cd "$LAB"
EXTRA=()
if [[ "${HEADLESS:-0}" == "1" ]]; then
  EXTRA+=(--headless)
fi
echo "[INFO] play run=$LOAD_RUN ckpt=$CHECKPOINT"
python scripts/getup/play.py \
  --task Getup-Twisted-T800-v0 \
  --num_envs 1 \
  --device cuda:0 \
  --load_run "$LOAD_RUN" \
  --checkpoint "$CHECKPOINT" \
  "${EXTRA[@]}"
