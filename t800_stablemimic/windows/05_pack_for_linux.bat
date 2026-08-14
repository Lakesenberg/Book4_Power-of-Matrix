@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."
call "windows\local_config.bat"

set OUT=%~dp0..\handoff_windows_to_linux
if exist "%OUT%" rmdir /S /Q "%OUT%"
mkdir "%OUT%"

echo [INFO] 打包 Windows checkpoint → %OUT%
%ISAAC_PYTHON% "%~dp0..\scripts\pack_checkpoints.py" ^
  --lab-root "%ENGINEAI_RL_LAB%" ^
  --out-dir "%OUT%" ^
  --experiment tracking_t800 ^
  --stage WIN1_TRACKING

if errorlevel 1 exit /b 1

%ISAAC_PYTHON% "%~dp0..\scripts\validate_handoff.py" --handoff-root "%OUT%"
if errorlevel 1 exit /b 1

echo.
echo [OK] 把整个文件夹拷到 Linux:
echo      %OUT%
echo 合并进 Linux 上的 engineai_rl_lab 根目录后，看 CHECKPOINT_HANDOFF.md
echo.
exit /b 0
