import gymnasium as gym

from . import agents, getup_env_cfg

gym.register(
    id="Getup-Twisted-T800-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": getup_env_cfg.T800GetupEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:T800GetupPPORunnerCfg",
    },
)
