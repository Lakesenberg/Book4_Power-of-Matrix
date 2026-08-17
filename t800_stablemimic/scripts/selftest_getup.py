"""Validate get-up pose catalog and overlay copy (no Isaac required)."""

from __future__ import annotations

import ast
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "getup"))

from apply_getup_overlay import apply  # noqa: E402
from poses import FAMILIES, STAGE_WEIGHTS, T800_JOINTS, family_names, stage_weights, validate_catalog  # noqa: E402


def test_catalog() -> None:
    errors = validate_catalog()
    assert not errors, errors
    assert set(T800_JOINTS) >= set().union(*(set(spec["joints"]) for spec in FAMILIES.values()))
    for stage in range(len(STAGE_WEIGHTS)):
        weights = stage_weights(stage)
        assert abs(sum(weights.values()) - 1.0) < 1e-6
        assert set(family_names(stage)) == set(weights)
        assert "sit" not in family_names(5)
        assert "mid_contact" in family_names(5)
        assert "prone" not in family_names(0)
        assert "prone" not in family_names(2)


def test_overlay_registers_task() -> None:
    init_py = ROOT / "getup" / "overlay" / "tasks" / "getup" / "config" / "t800" / "__init__.py"
    tree = ast.parse(init_py.read_text(encoding="utf-8"))
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in getattr(node, "keywords", []):
                if kw.arg == "id" and isinstance(kw.value, ast.Constant):
                    if kw.value.value == "Getup-Twisted-T800-v0":
                        found = True
    assert found, "Getup-Twisted-T800-v0 not registered"


def test_apply_overlay() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="t800_getup_"))
    try:
        tasks = tmp / "source" / "engineai_rl_lab" / "engineai_rl_lab" / "tasks"
        tasks.mkdir(parents=True)
        written = apply(tmp)
        dest = tmp / "source" / "engineai_rl_lab" / "engineai_rl_lab" / "tasks" / "getup"
        assert dest.is_dir()
        assert (dest / "poses.py").is_file()
        assert (tmp / "scripts" / "getup" / "train.py").is_file()
        text = (dest / "config" / "t800" / "__init__.py").read_text(encoding="utf-8")
        assert "Getup-Twisted-T800-v0" in text
        assert all(p.exists() for p in written)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    test_catalog()
    test_overlay_registers_task()
    test_apply_overlay()
    print("[OK] get-up catalog + overlay selftest passed")
    print("     families:", ", ".join(sorted(FAMILIES)))
    print("     stage0:", family_names(0))
    print("     stage5:", family_names(5))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
