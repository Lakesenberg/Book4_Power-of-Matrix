@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
echo ============================================
echo  T800 Windows 训练环境检查 / 拉取官方仓库
echo ============================================

if not exist "windows\local_config.bat" (
  copy /Y "windows\local_config.example.bat" "windows\local_config.bat" >nul
  echo [INFO] 已生成 windows\local_config.bat ，请按本机路径改 ISAAC_PYTHON
)

call "windows\local_config.bat"

where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] 需要 Git
  exit /b 1
)

if not exist "%ENGINEAI_RL_LAB%\scripts\tracking\train.py" (
  echo [INFO] 克隆 engineai_rl_lab ...
  mkdir "%~dp0..\vendor" 2>nul
  git clone --depth 1 https://github.com/engineai-robotics/engineai_rl_lab.git "%ENGINEAI_RL_LAB%"
  if errorlevel 1 (
    echo [ERROR] clone 失败
    exit /b 1
  )
) else (
  echo [OK] 已存在 %ENGINEAI_RL_LAB%
)

echo.
echo 接下来请在「已安装 Isaac Sim 5.1 + Isaac Lab 2.3.2」的环境里执行:
echo   1. 激活 Isaac Lab 的 Python 环境
echo   2. cd %ENGINEAI_RL_LAB%
echo   3. pip install -e source\engineai_rl_lab
echo   4. 把 windows\local_config.bat 里的 ISAAC_PYTHON 改成该环境的 python
echo   5. 运行 02_convert_motion.bat
echo.
echo Isaac Lab 安装: https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/installation/index.html
echo 必须钉死 commit: c22775241e28f465fe345fa1a482ad6d29d712b0
echo Windows 请先开启长路径，驱动建议生产分支 580.88
echo 本阶段只支持单卡，不要加多 GPU
echo.
exit /b 0
