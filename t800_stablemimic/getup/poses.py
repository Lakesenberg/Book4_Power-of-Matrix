"""Static twisted fallen-pose catalog for T800 get-up.

No Isaac / torch dependency. Overlay copies this next to the env so reset
can sample families A–E plus an easier sit stage.
"""

from __future__ import annotations

import math
from typing import Any

T800_JOINTS: tuple[str, ...] = (
    "J00_HIP_PITCH_L",
    "J01_HIP_ROLL_L",
    "J02_HIP_YAW_L",
    "J03_KNEE_PITCH_L",
    "J04_ANKLE_PITCH_L",
    "J05_ANKLE_ROLL_L",
    "J06_HIP_PITCH_R",
    "J07_HIP_ROLL_R",
    "J08_HIP_YAW_R",
    "J09_KNEE_PITCH_R",
    "J10_ANKLE_PITCH_R",
    "J11_ANKLE_ROLL_R",
    "J12_TORSO_YAW",
    "J13_SHOULDER_PITCH_L",
    "J14_SHOULDER_ROLL_L",
    "J15_SHOULDER_YAW_L",
    "J16_ELBOW_PITCH_L",
    "J17_ELBOW_YAW_L",
    "J18_SHOULDER_PITCH_R",
    "J19_SHOULDER_ROLL_R",
    "J20_SHOULDER_YAW_R",
    "J21_ELBOW_PITCH_R",
    "J22_ELBOW_YAW_R",
    "J23_HEAD_PITCH",
    "J24_HEAD_YAW",
)

STAND_HEIGHT = 1.06

# Conservative clamps so random twists stay inside typical T800 ranges.
JOINT_CLAMP: dict[str, tuple[float, float]] = {
    "J00_HIP_PITCH_L": (-1.8, 0.6),
    "J06_HIP_PITCH_R": (-1.8, 0.6),
    "J01_HIP_ROLL_L": (-0.7, 0.7),
    "J07_HIP_ROLL_R": (-0.7, 0.7),
    "J02_HIP_YAW_L": (-0.9, 0.9),
    "J08_HIP_YAW_R": (-0.9, 0.9),
    "J03_KNEE_PITCH_L": (0.0, 2.2),
    "J09_KNEE_PITCH_R": (0.0, 2.2),
    "J04_ANKLE_PITCH_L": (-0.8, 0.8),
    "J10_ANKLE_PITCH_R": (-0.8, 0.8),
    "J05_ANKLE_ROLL_L": (-0.4, 0.4),
    "J11_ANKLE_ROLL_R": (-0.4, 0.4),
    "J12_TORSO_YAW": (-1.3, 1.3),
    "J13_SHOULDER_PITCH_L": (-2.4, 1.8),
    "J18_SHOULDER_PITCH_R": (-2.4, 1.8),
    "J14_SHOULDER_ROLL_L": (-0.3, 1.6),
    "J19_SHOULDER_ROLL_R": (-1.6, 0.3),
    "J15_SHOULDER_YAW_L": (-1.4, 1.4),
    "J20_SHOULDER_YAW_R": (-1.4, 1.4),
    "J16_ELBOW_PITCH_L": (-2.0, 0.3),
    "J21_ELBOW_PITCH_R": (-2.0, 0.3),
    "J17_ELBOW_YAW_L": (-1.4, 1.4),
    "J22_ELBOW_YAW_R": (-1.4, 1.4),
    "J23_HEAD_PITCH": (-0.6, 0.6),
    "J24_HEAD_YAW": (-0.8, 0.8),
}

# Root euler is XYZ, Isaac wxyz later. z is world height (keep above ground).
# sit = easier recline; others are static ground poses (no push-to-fall).
FAMILIES: dict[str, dict[str, Any]] = {
    "sit": {
        "label": "sit_recline",
        "root_z": 0.52,
        "root_z_noise": 0.06,
        "roll": 0.0,
        "pitch": 0.75,
        "euler_noise": 0.12,
        "joints": {
            "J00_HIP_PITCH_L": -0.85,
            "J06_HIP_PITCH_R": -0.85,
            "J03_KNEE_PITCH_L": 1.15,
            "J09_KNEE_PITCH_R": 1.15,
            "J04_ANKLE_PITCH_L": -0.25,
            "J10_ANKLE_PITCH_R": -0.25,
            "J13_SHOULDER_PITCH_L": 0.25,
            "J18_SHOULDER_PITCH_R": 0.25,
            "J16_ELBOW_PITCH_L": -0.6,
            "J21_ELBOW_PITCH_R": -0.6,
        },
    },
    "supine": {
        "label": "A_supine",
        "root_z": 0.34,
        "root_z_noise": 0.03,
        "roll": 0.0,
        "pitch": 1.42,
        "euler_noise": 0.18,
        "joints": {
            "J00_HIP_PITCH_L": -0.20,
            "J06_HIP_PITCH_R": -0.18,
            "J03_KNEE_PITCH_L": 0.45,
            "J09_KNEE_PITCH_R": 0.40,
            "J14_SHOULDER_ROLL_L": 0.45,
            "J19_SHOULDER_ROLL_R": -0.45,
            "J13_SHOULDER_PITCH_L": 0.15,
            "J18_SHOULDER_PITCH_R": 0.10,
            "J16_ELBOW_PITCH_L": -0.35,
            "J21_ELBOW_PITCH_R": -0.35,
        },
    },
    "side_left": {
        "label": "C_side_left",
        "root_z": 0.32,
        "root_z_noise": 0.03,
        "roll": 1.40,
        "pitch": 0.10,
        "euler_noise": 0.16,
        "joints": {
            "J00_HIP_PITCH_L": -0.35,
            "J06_HIP_PITCH_R": -0.55,
            "J01_HIP_ROLL_L": 0.25,
            "J07_HIP_ROLL_R": 0.15,
            "J03_KNEE_PITCH_L": 0.55,
            "J09_KNEE_PITCH_R": 0.90,
            "J13_SHOULDER_PITCH_L": -0.40,
            "J18_SHOULDER_PITCH_R": 0.50,
            "J14_SHOULDER_ROLL_L": 0.20,
            "J16_ELBOW_PITCH_L": -0.20,
            "J21_ELBOW_PITCH_R": -0.80,
        },
    },
    "side_right": {
        "label": "C_side_right",
        "root_z": 0.32,
        "root_z_noise": 0.03,
        "roll": -1.40,
        "pitch": 0.10,
        "euler_noise": 0.16,
        "joints": {
            "J00_HIP_PITCH_L": -0.55,
            "J06_HIP_PITCH_R": -0.35,
            "J01_HIP_ROLL_L": -0.15,
            "J07_HIP_ROLL_R": -0.25,
            "J03_KNEE_PITCH_L": 0.90,
            "J09_KNEE_PITCH_R": 0.55,
            "J13_SHOULDER_PITCH_L": 0.50,
            "J18_SHOULDER_PITCH_R": -0.40,
            "J19_SHOULDER_ROLL_R": -0.20,
            "J16_ELBOW_PITCH_L": -0.80,
            "J21_ELBOW_PITCH_R": -0.20,
        },
    },
    "prone": {
        "label": "B_prone",
        "root_z": 0.34,
        "root_z_noise": 0.03,
        "roll": 0.0,
        "pitch": -1.42,
        "euler_noise": 0.16,
        "joints": {
            "J00_HIP_PITCH_L": 0.15,
            "J06_HIP_PITCH_R": 0.12,
            "J03_KNEE_PITCH_L": 0.35,
            "J09_KNEE_PITCH_R": 0.38,
            "J13_SHOULDER_PITCH_L": -0.70,
            "J18_SHOULDER_PITCH_R": -0.70,
            "J14_SHOULDER_ROLL_L": 0.35,
            "J19_SHOULDER_ROLL_R": -0.35,
            "J16_ELBOW_PITCH_L": -1.10,
            "J21_ELBOW_PITCH_R": -1.10,
        },
    },
    "cross": {
        "label": "D_cross_twist",
        "root_z": 0.34,
        "root_z_noise": 0.03,
        "roll": 0.25,
        "pitch": 1.28,
        "euler_noise": 0.20,
        "joints": {
            "J00_HIP_PITCH_L": -0.55,
            "J06_HIP_PITCH_R": 0.10,
            "J02_HIP_YAW_L": 0.55,
            "J08_HIP_YAW_R": -0.65,
            "J03_KNEE_PITCH_L": 1.15,
            "J09_KNEE_PITCH_R": 0.35,
            "J12_TORSO_YAW": 0.70,
            "J13_SHOULDER_PITCH_L": 0.40,
            "J18_SHOULDER_PITCH_R": -0.30,
            "J15_SHOULDER_YAW_L": 0.40,
            "J20_SHOULDER_YAW_R": -0.35,
        },
    },
    "mid_contact": {
        "label": "E_mid_contact",
        "root_z": 0.32,
        "root_z_noise": 0.025,
        "roll": 0.55,
        "pitch": 1.15,
        "euler_noise": 0.18,
        "joints": {
            "J00_HIP_PITCH_L": -0.40,
            "J06_HIP_PITCH_R": -0.15,
            "J03_KNEE_PITCH_L": 0.85,
            "J09_KNEE_PITCH_R": 0.30,
            "J13_SHOULDER_PITCH_L": -1.40,
            "J14_SHOULDER_ROLL_L": 0.70,
            "J16_ELBOW_PITCH_L": -1.50,
            "J18_SHOULDER_PITCH_R": 0.35,
            "J12_TORSO_YAW": -0.45,
        },
    },
}

# HoST-style: do not mix supine+prone on day one.
# 0 sit+supine → 1 supine → 2 +side → 3 +prone → 4 +cross → 5 +mid-contact
STAGE_WEIGHTS: tuple[dict[str, float], ...] = (
    {"sit": 0.55, "supine": 0.45},
    {"supine": 1.0},
    {"supine": 0.40, "side_left": 0.30, "side_right": 0.30},
    {"supine": 0.25, "side_left": 0.20, "side_right": 0.20, "prone": 0.35},
    {
        "supine": 0.18,
        "side_left": 0.16,
        "side_right": 0.16,
        "prone": 0.22,
        "cross": 0.28,
    },
    {
        "supine": 0.14,
        "side_left": 0.14,
        "side_right": 0.14,
        "prone": 0.16,
        "cross": 0.20,
        "mid_contact": 0.22,
    },
)

# env.common_step_counter thresholds (control steps, not PPO iters).
STAGE_MIN_STEPS: tuple[int, ...] = (0, 40000, 90000, 160000, 250000, 360000)
NUM_STAGES = len(STAGE_WEIGHTS)


def clamp_joint(name: str, value: float) -> float:
    lo, hi = JOINT_CLAMP.get(name, (-math.pi, math.pi))
    return max(lo, min(hi, value))


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        raise ValueError(f"stage weights must be positive: {weights}")
    return {k: v / total for k, v in weights.items()}


def stage_weights(stage: int) -> dict[str, float]:
    idx = max(0, min(int(stage), NUM_STAGES - 1))
    return normalize_weights(dict(STAGE_WEIGHTS[idx]))


def family_names(stage: int) -> tuple[str, ...]:
    return tuple(stage_weights(stage).keys())


def validate_catalog() -> list[str]:
    errors: list[str] = []
    known = set(T800_JOINTS)
    for fam, spec in FAMILIES.items():
        for joint in spec["joints"]:
            if joint not in known:
                errors.append(f"{fam}: unknown joint {joint}")
        if spec["root_z"] < 0.28:
            errors.append(f"{fam}: root_z too low ({spec['root_z']})")
    for i, weights in enumerate(STAGE_WEIGHTS):
        for name in weights:
            if name not in FAMILIES:
                errors.append(f"stage {i}: unknown family {name}")
        total = sum(weights.values())
        if abs(total - 1.0) > 1e-6:
            errors.append(f"stage {i}: weights sum {total}, expected 1")
    if len(STAGE_MIN_STEPS) != NUM_STAGES:
        errors.append("STAGE_MIN_STEPS length mismatch")
    return errors
