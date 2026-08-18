# 在 PowerShell 里运行本文件（不要在 C:\Windows\System32 下直接敲 01_setup.bat）
# 用法（仓库已经在磁盘上时）:
#   cd <你的>\Book4_Power-of-Matrix\t800_stablemimic
#   powershell -ExecutionPolicy Bypass -File .\Start-Here.ps1

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$windowsDir = Join-Path $here "windows"
$setupBat = Join-Path $windowsDir "01_setup.bat"

Write-Host ""
Write-Host "当前目录: $(Get-Location)"
Write-Host "脚本位置: $here"
Write-Host ""

if ((Get-Location).Path -match '\\[Ww]indows\\[Ss]ystem32$') {
    Write-Host "[错误] 你现在在 C:\Windows\System32。" -ForegroundColor Red
    Write-Host "这是系统目录，仓库不在这里。不要在这里 cd t800_stablemimic。"
    Write-Host ""
    Write-Host "请先把仓库克隆到用户目录，例如："
    Write-Host '  cd $HOME\Documents'
    Write-Host "  git clone -b cursor/t800-windows-train-2191 https://github.com/Lakesenberg/Book4_Power-of-Matrix.git"
    Write-Host "  cd Book4_Power-of-Matrix\t800_stablemimic"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\Start-Here.ps1"
    exit 1
}

if (-not (Test-Path $setupBat)) {
    Write-Host "[错误] 找不到 $setupBat" -ForegroundColor Red
    Write-Host "请先 checkout 分支 cursor/t800-windows-train-2191"
    exit 1
}

Write-Host "[OK] 将运行 01_setup.bat （PowerShell 里必须写成 .\xxx.bat）"
Set-Location $windowsDir
& cmd.exe /c "01_setup.bat"
exit $LASTEXITCODE
