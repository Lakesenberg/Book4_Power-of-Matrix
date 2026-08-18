"""Rewrite EngineAI robot USD paths to absolute so Isaac Kit cwd cannot break them."""

from __future__ import annotations

import argparse
from pathlib import Path

TARGETS = (
    Path("source/engineai_rl_lab/engineai_rl_lab/tasks/tracking/robots/t800.py"),
    Path("source/engineai_rl_lab/engineai_rl_lab/tasks/tracking/robots/pm01.py"),
)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "T800_USD_ABS" in text or "PM01_USD_ABS" in text:
        print(f"[skip] already patched: {path}")
        return False

    marker = "from isaaclab.utils import configclass"
    inject = """from isaaclab.utils import configclass
from pathlib import Path as _Path

_ASSET_DIR = _Path(__file__).resolve().parents[3] / "assets"
T800_USD_ABS = str(_ASSET_DIR / "t800" / "serial_t800.usd")
PM01_USD_ABS = str(_ASSET_DIR / "pm01" / "serial_pm01_edu.usd")
"""
    if marker not in text:
        raise SystemExit(f"unexpected file layout: {path}")
    text = text.replace(marker, inject, 1)
    text = text.replace(
        'usd_path="source/engineai_rl_lab/engineai_rl_lab/assets/t800/serial_t800.usd"',
        "usd_path=T800_USD_ABS",
    )
    text = text.replace(
        'usd_path="source/engineai_rl_lab/engineai_rl_lab/assets/pm01/serial_pm01_edu.usd"',
        "usd_path=PM01_USD_ABS",
    )
    path.write_text(text, encoding="utf-8")
    print(f"[ok] patched {path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", type=Path, required=True)
    args = parser.parse_args()
    changed = False
    for rel in TARGETS:
        path = args.lab_root / rel
        if not path.is_file():
            print(f"[warn] missing {path}")
            continue
        changed = patch_file(path) or changed
    usd = args.lab_root / "source/engineai_rl_lab/engineai_rl_lab/assets/t800/serial_t800.usd"
    print("[info] usd exists" if usd.is_file() else f"[warn] usd missing: {usd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
