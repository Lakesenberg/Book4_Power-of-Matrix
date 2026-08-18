@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
call "windows\local_config.bat"

if not exist "%ENGINEAI_RL_LAB%\datasets\tracking\t800\dance_t800.csv" (
  echo [ERROR] 找不到 dance_t800.csv
  exit /b 1
)

echo [INFO] csv → npz （会启动 Isaac Sim，请耐心等待）
cd /d "%ENGINEAI_RL_LAB%"
%ISAAC_PYTHON% scripts\csv_to_npz.py --robot t800 --input_fps 30 --headless -f datasets\tracking\t800\dance_t800.csv
if errorlevel 1 (
  echo [ERROR] 转换失败。确认 ISAAC_PYTHON 指向 Isaac Lab 环境，且已 pip install -e source\engineai_rl_lab
  exit /b 1
)
echo [OK] 应生成 datasets\tracking\t800\dance_t800.npz
exit /b 0
