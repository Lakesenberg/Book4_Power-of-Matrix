@echo off
REM 复制为 local_config.bat 后按本机路径改
REM 不要把 local_config.bat 提交进 git

REM Isaac Lab 虚拟环境的 python（激活后 where python）
set ISAAC_PYTHON=python

REM 官方训练仓库根目录（01_setup.bat 会自动 clone）
set ENGINEAI_RL_LAB=%~dp0..\vendor\engineai_rl_lab

REM 显存 16GB 用 1024；24GB 用 2048；官方默认 4096 在 Windows 上容易爆
set NUM_ENVS=2048

REM 单卡
set RL_DEVICE=cuda:0
