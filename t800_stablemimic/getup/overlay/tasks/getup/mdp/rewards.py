from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import ContactSensor

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def _asset(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg) -> Articulation:
    return env.scene[asset_cfg.name]


def projected_gravity_xy_exp(
    env: ManagerBasedRLEnv,
    std: float = 0.5,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Upright: body-frame gravity xy should be near 0."""
    asset = _asset(env, asset_cfg)
    xy = asset.data.projected_gravity_b[:, :2]
    return torch.exp(-torch.sum(torch.square(xy), dim=-1) / std**2)


def base_height_exp(
    env: ManagerBasedRLEnv,
    target_height: float = 1.02,
    std: float = 0.28,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    asset = _asset(env, asset_cfg)
    height = asset.data.root_pos_w[:, 2]
    return torch.exp(-torch.square(height - target_height) / std**2)


def standing_stable(
    env: ManagerBasedRLEnv,
    min_height: float = 0.88,
    max_tilt: float = 0.45,
    max_lin_vel: float = 0.55,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    asset = _asset(env, asset_cfg)
    height_ok = asset.data.root_pos_w[:, 2] > min_height
    tilt = torch.linalg.norm(asset.data.projected_gravity_b[:, :2], dim=-1)
    tilt_ok = tilt < max_tilt
    speed = torch.linalg.norm(asset.data.root_lin_vel_w[:, :2], dim=-1)
    still_ok = speed < max_lin_vel
    return (height_ok & tilt_ok & still_ok).float()


def fast_stand_bonus(
    env: ManagerBasedRLEnv,
    min_height: float = 0.88,
    max_tilt: float = 0.45,
    max_lin_vel: float = 0.55,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """More reward for being up early in the episode."""
    standing = standing_stable(env, min_height, max_tilt, max_lin_vel, asset_cfg)
    time_frac = torch.clamp(env.episode_length_buf.float() * env.step_dt / env.max_episode_length_s, 0.0, 1.0)
    return standing * (1.0 - time_frac)


def first_stand_bonus(
    env: ManagerBasedRLEnv,
    min_height: float = 0.88,
    max_tilt: float = 0.45,
    max_lin_vel: float = 0.55,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """One-shot bonus the first time the robot is stably up (encourages speed)."""
    if not hasattr(env, "getup_stood_once"):
        env.getup_stood_once = torch.zeros(env.scene.num_envs, dtype=torch.bool, device=env.device)
    standing = standing_stable(env, min_height, max_tilt, max_lin_vel, asset_cfg).bool()
    first = standing & (~env.getup_stood_once)
    env.getup_stood_once = env.getup_stood_once | standing
    if hasattr(env, "getup_stand_hold"):
        env.getup_stand_hold = torch.where(
            standing,
            env.getup_stand_hold + env.step_dt,
            torch.zeros_like(env.getup_stand_hold),
        )
    return first.float()


def lin_vel_l2_when_standing(
    env: ManagerBasedRLEnv,
    min_height: float = 0.88,
    max_tilt: float = 0.45,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    asset = _asset(env, asset_cfg)
    standing = (asset.data.root_pos_w[:, 2] > min_height) & (
        torch.linalg.norm(asset.data.projected_gravity_b[:, :2], dim=-1) < max_tilt
    )
    speed = torch.sum(torch.square(asset.data.root_lin_vel_w[:, :2]), dim=-1)
    return speed * standing.float()


def fly_height(
    env: ManagerBasedRLEnv,
    max_height: float = 1.45,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    asset = _asset(env, asset_cfg)
    return torch.clamp(asset.data.root_pos_w[:, 2] - max_height, min=0.0)


def joint_vel_l2(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    asset = _asset(env, asset_cfg)
    return torch.sum(torch.square(asset.data.joint_vel[:, asset_cfg.joint_ids]), dim=-1)


def head_contact(
    env: ManagerBasedRLEnv,
    threshold: float = 1.0,
    sensor_cfg: SceneEntityCfg = SceneEntityCfg("contact_forces", body_names=[".*HEAD.*"]),
) -> torch.Tensor:
    sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    net = sensor.data.net_forces_w[:, sensor_cfg.body_ids]
    force = torch.linalg.norm(net, dim=-1)
    return torch.any(force > threshold, dim=-1).float()
