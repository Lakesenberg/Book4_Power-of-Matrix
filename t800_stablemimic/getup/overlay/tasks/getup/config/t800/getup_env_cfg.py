from isaaclab.utils import configclass

from engineai_rl_lab.tasks.getup.getup_env_cfg import GetupEnvCfg
from engineai_rl_lab.tasks.tracking.robots.t800 import T800_ACTION_SCALE, T800_CYLINDER_CFG


@configclass
class T800GetupEnvCfg(GetupEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.robot = T800_CYLINDER_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.env_spacing = 3.5
        self.actions.joint_pos.scale = T800_ACTION_SCALE
