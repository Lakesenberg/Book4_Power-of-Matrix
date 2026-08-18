"""Create a fake run and verify pack + validate (no Isaac required)."""

from __future__ import annotations

import json
import pickle
import shutil
import tempfile
from pathlib import Path

from pack_checkpoints import pack
from validate_handoff import validate


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="t800_handoff_"))
    try:
        lab = tmp / "lab"
        run = lab / "logs" / "rsl_rl" / "tracking_t800" / "2026-08-14_00-00-00_win1_tracking"
        (run / "params").mkdir(parents=True)
        (run / "model_8000.pt").write_bytes(b"fake-pt")
        (run / "params" / "env.yaml").write_text("task: t800\n", encoding="utf-8")
        (run / "params" / "agent.yaml").write_text("algo: ppo\n", encoding="utf-8")
        pickle.dump({"ok": True}, (run / "params" / "env.pkl").open("wb"))
        pickle.dump({"ok": True}, (run / "params" / "agent.pkl").open("wb"))
        motion = lab / "datasets" / "tracking" / "t800"
        motion.mkdir(parents=True)
        (motion / "dance_t800.npz").write_bytes(b"fake-npz")
        (motion / "dance_t800.csv").write_text("t,q\n", encoding="utf-8")

        out = tmp / "handoff"
        manifest = pack(lab, out, stage="WIN1_TRACKING")
        assert manifest["checkpoint_name"] == "model_8000.pt"
        assert manifest["iteration"] == 8000
        errors = validate(out)
        assert not errors, errors
        loaded = json.loads((out / "handoff" / "manifest.json").read_text(encoding="utf-8"))
        assert "linux_resume_cmd" in loaded
        print("[OK] pack/validate selftest passed")
        print("     sample resume:", loaded["linux_resume_cmd"])
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
