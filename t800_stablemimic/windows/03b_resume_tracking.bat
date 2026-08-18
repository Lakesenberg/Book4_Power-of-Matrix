@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
call "windows\local_config.bat"

REM 可选: 同任务续训。不填则自动找最新 run / 最新 model_*.pt
if "%LOAD_RUN%"=="" set LOAD_RUN=
if "%CHECKPOINT%"=="" set CHECKPOINT=

cd /d "%~dp0\..\scripts"
for /f "usebackq tokens=*" %%i in (`%ISAAC_PYTHON% find_latest_ckpt.py --lab-root "%ENGINEAI_RL_LAB%" --experiment tracking_t800 --json`) do set CKPT_JSON=%%i

echo [INFO] 续训 WIN2 ，从最新 checkpoint resume
echo        若要指定: set LOAD_RUN=2026-xx-xx_xx-xx-xx_win1_tracking
echo                  set CHECKPOINT=model_10000.pt
echo.

cd /d "%ENGINEAI_RL_LAB%"
if "%LOAD_RUN%"=="" (
  %ISAAC_PYTHON% scripts\tracking\train.py ^
    --task Tracking-Flat-T800-Wo-State-Estimation-v0 ^
    --headless ^
    --num_envs %NUM_ENVS% ^
    --device %RL_DEVICE% ^
    --max_iterations 10000 ^
    --resume True ^
    --run_name win2_resume ^
    --motion_file datasets\tracking\t800\dance_t800.npz
) else (
  %ISAAC_PYTHON% scripts\tracking\train.py ^
    --task Tracking-Flat-T800-Wo-State-Estimation-v0 ^
    --headless ^
    --num_envs %NUM_ENVS% ^
    --device %RL_DEVICE% ^
    --max_iterations 10000 ^
    --resume True ^
    --load_run %LOAD_RUN% ^
    --checkpoint %CHECKPOINT% ^
    --run_name win2_resume ^
    --motion_file datasets\tracking\t800\dance_t800.npz
)
exit /b %ERRORLEVEL%
