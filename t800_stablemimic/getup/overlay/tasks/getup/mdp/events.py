from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch

from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import quat_from_euler_xyz

from engineai_rl_lab.tasks.getup.poses import (
    FAMILIES,
    JOINT_CLAMP,
    T800_JOINTS,
    family_names,
    stage_weights,
)

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedEnv

JOINT_LO = {k: v[0] for k, v in JOINT_CLAMP.items()}
JOINT_HI = {k: v[1] for k, v in JOINT_CLAMP.items()}


def _ensure_getup_state(env: ManagerBasedEnv, device: torch.device, num_envs: int) -> None:
    if not hasattr(env, "getup_stage"):
        env.getup_stage = 0
    if not hasattr(env, "getup_family_id"):
        env.getup_family_id = torch.zeros(num_envs, dtype=torch.long, device=device)
    if not hasattr(env, "getup_stand_hold"):
        env.getup_stand_hold = torch.zeros(num_envs, device=device)
    if not hasattr(env, "getup_stood_once"):
        env.getup_stood_once = torch.zeros(num_envs, dtype=torch.bool, device=device)
    if not hasattr(env, "getup_success_ema"):
        env.getup_success_ema = 0.0
    if not hasattr(env, "getup_success_count"):
        env.getup_success_count = 0
    if not hasattr(env, "getup_episode_count"):
        env.getup_episode_count = 0


def _joint_index_map(asset: Articulation) -> dict[str, int]:
    return {name: i for i, name in enumerate(asset.joint_names)}


def reset_to_static_twisted_pose(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    joint_noise: float = 0.08,
    yaw_range: tuple[float, float] = (-math.pi, math.pi),
) -> None:
    """Reset onto a static ground pose. No dance trajectory, no push-to-fall."""
    asset: Articulation = env.scene[asset_cfg.name]
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)
    if env_ids.numel() == 0:
        return

    _ensure_getup_state(env, asset.device, env.scene.num_envs)
    # Skip the first simulator reset (episode length is still 0).
    if hasattr(env, "episode_length_buf"):
        finished = env.episode_length_buf[env_ids] > 1
    else:
        finished = torch.ones(env_ids.numel(), dtype=torch.bool, device=asset.device)
    if torch.any(finished):
        done_ids = env_ids[finished]
        success = (env.getup_stand_hold[done_ids] >= 0.6) | env.getup_stood_once[done_ids]
        n_done = int(done_ids.numel())
        n_ok = int(success.sum().item())
        env.getup_episode_count += n_done
        env.getup_success_count += n_ok
        env.getup_success_ema = 0.9 * float(env.getup_success_ema) + 0.1 * (n_ok / n_done)
    env.getup_stand_hold[env_ids] = 0.0
    env.getup_stood_once[env_ids] = False

    names = family_names(env.getup_stage)
    weights = stage_weights(env.getup_stage)
    weight_t = torch.tensor([weights[n] for n in names], device=asset.device, dtype=torch.float32)
    choice = torch.multinomial(weight_t.expand(env_ids.numel(), -1), 1).squeeze(-1)

    root = asset.data.default_root_state[env_ids].clone()
    root[:, 0:3] = env.scene.env_origins[env_ids]
    joint_pos = asset.data.default_joint_pos[env_ids].clone()
    joint_vel = torch.zeros_like(joint_pos)
    name_to_idx = _joint_index_map(asset)

    for fam_i, fam in enumerate(names):
        mask = choice == fam_i
        if not torch.any(mask):
            continue
        ids = env_ids[mask]
        spec = FAMILIES[fam]
        n = int(mask.sum().item())
        e_noise = spec["euler_noise"]
        height = spec["root_z"] + (torch.rand(n, device=asset.device) * 2 - 1) * spec["root_z_noise"]
        # Drop from above the ground. Embedding a 1m-tall pitched body at z=0.3
        # makes CPU PhysX hang on the first contact-resolution step.
        height = torch.clamp(height, min=0.55, max=0.90)
        roll = spec["roll"] + (torch.rand(n, device=asset.device) * 2 - 1) * e_noise
        pitch = spec["pitch"] + (torch.rand(n, device=asset.device) * 2 - 1) * e_noise
        yaw = torch.empty(n, device=asset.device).uniform_(yaw_range[0], yaw_range[1])
        quat = quat_from_euler_xyz(roll, pitch, yaw)

        root[mask, 2] = height
        root[mask, 3:7] = quat
        env.getup_family_id[ids] = fam_i

        local = joint_pos[mask]
        for joint_name in T800_JOINTS:
            if joint_name not in name_to_idx:
                continue
            j = name_to_idx[joint_name]
            base = spec["joints"].get(joint_name, float(asset.data.default_joint_pos[0, j].item()))
            noise = (torch.rand(n, device=asset.device) * 2 - 1) * joint_noise
            local[:, j] = torch.clamp(
                local.new_full((n,), base) + noise,
                min=JOINT_LO.get(joint_name, -math.pi),
                max=JOINT_HI.get(joint_name, math.pi),
            )
        joint_pos[mask] = local

    asset.write_root_pose_to_sim(root[:, :7], env_ids)
    asset.write_root_velocity_to_sim(torch.zeros(env_ids.numel(), 6, device=asset.device), env_ids)
    asset.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)
    if not getattr(env, "_getup_reset_logged", False):
        env._getup_reset_logged = True
        print(
            f"[getup] first reset: n={int(env_ids.numel())} stage={env.getup_stage} "
            f"families={list(names)} (drop-in, not embedded)",
            flush=True,
        )
