@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
call "windows\local_config.bat"

if not exist "%ENGINEAI_RL_LAB%\datasets\tracking\t800\dance_t800.npz" (
  echo [ERROR] 先跑 02_convert_motion.bat 生成 dance_t800.npz
  exit /b 1
)

echo ============================================
echo  WIN1 官方 T800 tracking （Windows 单卡）
echo  task=Tracking-Flat-T800-Wo-State-Estimation-v0
echo  num_envs=%NUM_ENVS%  device=%RL_DEVICE%
echo ============================================
echo 关掉休眠。必须 --headless。显存不够把 local_config.bat 的 NUM_ENVS 改成 1024。
echo.

cd /d "%ENGINEAI_RL_LAB%"
%ISAAC_PYTHON% scripts\tracking\train.py ^
  --task Tracking-Flat-T800-Wo-State-Estimation-v0 ^
  --headless ^
  --num_envs %NUM_ENVS% ^
  --device %RL_DEVICE% ^
  --max_iterations 20000 ^
  --run_name win1_tracking ^
  --motion_file datasets\tracking\t800\dance_t800.npz

if errorlevel 1 (
  echo [ERROR] 训练退出。看上方 Isaac / CUDA 报错。
  exit /b 1
)

echo [OK] 日志在 %ENGINEAI_RL_LAB%\logs\rsl_rl\tracking_t800\
echo      下一步: 04_play_check.bat 或直接 05_pack_for_linux.bat
exit /b 0
