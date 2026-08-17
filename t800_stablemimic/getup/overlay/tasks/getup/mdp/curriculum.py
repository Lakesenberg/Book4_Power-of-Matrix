from __future__ import annotations

from typing import TYPE_CHECKING

from engineai_rl_lab.tasks.getup.poses import NUM_STAGES, STAGE_MIN_STEPS, family_names

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv
    import torch


def advance_twisted_pose_stage(
    env: ManagerBasedRLEnv,
    env_ids: "torch.Tensor",
    success_threshold: float = 0.40,
    min_episodes: int = 80,
) -> float:
    """Unlock harder static families after enough successful fast stands.

    Stage order: sit+supine → supine → +side → +prone → +cross → +mid-contact.
    """
    if not hasattr(env, "getup_stage"):
        env.getup_stage = 0
    stage = int(env.getup_stage)
    if stage >= NUM_STAGES - 1:
        return float(stage)

    steps = int(getattr(env, "common_step_counter", 0))
    if steps < STAGE_MIN_STEPS[stage + 1]:
        return float(stage)
    episodes = int(getattr(env, "getup_episode_count", 0))
    ema = float(getattr(env, "getup_success_ema", 0.0))
    if episodes >= min_episodes and ema >= success_threshold:
        env.getup_stage = stage + 1
        names = ",".join(family_names(env.getup_stage))
        print(f"[getup] curriculum → stage {env.getup_stage} families={names} ema={ema:.2f}")
    return float(env.getup_stage)
