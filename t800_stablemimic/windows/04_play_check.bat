@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
call "windows\local_config.bat"

echo [INFO] 用 1 个环境回放最新 checkpoint（可去掉 --headless 看画面）
cd /d "%ENGINEAI_RL_LAB%"

REM play.py 用 --load_run / --checkpoint；不指定则请先改成你的 run 名
if "%LOAD_RUN%"=="" (
  echo [ERROR] 请先 set LOAD_RUN=logs 里 tracking_t800 下的文件夹名
  echo        例如 set LOAD_RUN=2026-08-14_12-00-00_win1_tracking
  echo        再 set CHECKPOINT=model_20000.pt
  dir /B /AD logs\rsl_rl\tracking_t800
  exit /b 1
)

%ISAAC_PYTHON% scripts\tracking\play.py ^
  --task Tracking-Flat-T800-Wo-State-Estimation-v0 ^
  --num_envs 1 ^
  --motion_file datasets\tracking\t800\dance_t800.npz ^
  --load_run %LOAD_RUN% ^
  --checkpoint %CHECKPOINT%
exit /b %ERRORLEVEL%
