from __future__ import annotations

from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise

from engineai_rl_lab.tasks.tracking.mdp.events import randomize_joint_default_pos, randomize_rigid_body_com
from engineai_rl_lab.tasks.tracking.tracking_env_cfg import MySceneCfg
import engineai_rl_lab.tasks.getup.mdp as mdp


@configclass
class CommandsCfg:
    """No dance / velocity command. Get-up is fully proprioceptive."""


@configclass
class ActionsCfg:
    joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot", joint_names=[".*"], use_default_offset=True
    )


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        projected_gravity = ObsTerm(func=mdp.projected_gravity, noise=Unoise(n_min=-0.05, n_max=0.05))
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel, noise=Unoise(n_min=-0.2, n_max=0.2))
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, noise=Unoise(n_min=-0.01, n_max=0.01))
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, noise=Unoise(n_min=-0.5, n_max=0.5))
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    @configclass
    class PrivilegedCfg(ObsGroup):
        projected_gravity = ObsTerm(func=mdp.projected_gravity)
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        joint_pos = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        actions = ObsTerm(func=mdp.last_action)
        height = ObsTerm(func=mdp.root_height)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()
    critic: PrivilegedCfg = PrivilegedCfg()


@configclass
class EventCfg:
    physics_material = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.4, 1.6),
            "dynamic_friction_range": (0.3, 1.2),
            "restitution_range": (0.0, 0.3),
            "num_buckets": 64,
        },
    )
    add_joint_default_pos = EventTerm(
        func=randomize_joint_default_pos,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=[".*"]),
            "pos_distribution_params": (-0.01, 0.01),
            "operation": "add",
        },
    )
    base_com = EventTerm(
        func=randomize_rigid_body_com,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="LINK_WAIST_YAW"),
            "com_range": {"x": (-0.04, 0.04), "y": (-0.04, 0.04), "z": (-0.04, 0.04)},
        },
    )
    reset_pose = EventTerm(
        func=mdp.reset_to_static_twisted_pose,
        mode="reset",
        params={"asset_cfg": SceneEntityCfg("robot"), "joint_noise": 0.08},
    )


@configclass
class RewardsCfg:
    upright = RewTerm(func=mdp.projected_gravity_xy_exp, weight=2.0, params={"std": 0.55})
    height = RewTerm(func=mdp.base_height_exp, weight=1.6, params={"target_height": 1.02, "std": 0.28})
    standing = RewTerm(func=mdp.standing_stable, weight=3.2)
    fast_stand = RewTerm(func=mdp.fast_stand_bonus, weight=2.4)
    first_stand = RewTerm(func=mdp.first_stand_bonus, weight=8.0)
    stand_drift = RewTerm(func=mdp.lin_vel_l2_when_standing, weight=-0.6)
    action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=-0.02)
    joint_vel_l2 = RewTerm(func=mdp.joint_vel_l2, weight=-0.001)
    joint_limit = RewTerm(
        func=mdp.joint_pos_limits,
        weight=-8.0,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*"])},
    )
    fly = RewTerm(func=mdp.fly_height, weight=-2.0, params={"max_height": 1.45})


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    fly_away = DoneTerm(func=mdp.base_too_high, params={"threshold": 1.7})
    explode = DoneTerm(func=mdp.base_too_fast, params={"threshold": 8.0})


@configclass
class CurriculumCfg:
    pose_stage = CurrTerm(func=mdp.advance_twisted_pose_stage)


@configclass
class GetupEnvCfg(ManagerBasedRLEnvCfg):
    scene: MySceneCfg = MySceneCfg(num_envs=256, env_spacing=3.5)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        self.decimation = 4
        # Short horizon: standing sooner collects more reward.
        self.episode_length_s = 6.0
        self.sim.dt = 0.005
        self.sim.render_interval = self.decimation
        self.sim.physics_material = self.scene.terrain.physics_material
        self.sim.physx.gpu_max_rigid_patch_count = 10 * 2**15
        self.viewer.eye = (2.0, 2.0, 1.2)
        self.viewer.origin_type = "asset_root"
        self.viewer.asset_name = "robot"
        self.scene.contact_forces.debug_vis = False
