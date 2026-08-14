# 从任意目录（包括 System32）进入 WSL 用户家目录。
# 在 PowerShell 里整段粘贴也可以，不必先 cd 到仓库。

Set-Location $HOME
Write-Host "Windows 当前目录已改为: $(Get-Location)" -ForegroundColor Green

$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $wsl) {
    Write-Host "未找到 wsl。请先以管理员 PowerShell 运行:" -ForegroundColor Red
    Write-Host "  wsl --install -d Ubuntu-22.04"
    Write-Host "然后重启电脑，开始菜单打开 Ubuntu，不要再回 System32。"
    exit 1
}

Write-Host "进入 WSL。之后所有命令都在 Linux 里敲，提示符应类似 user@PC:~$"
wsl -e bash -lc "cd ~ && pwd && echo '已在 WSL 家目录。下一步看 t800_stablemimic/wsl/README.md'"
wsl
