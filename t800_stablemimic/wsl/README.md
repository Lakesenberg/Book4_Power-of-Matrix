# 在 Windows 的 WSL 里训 T800（推荐你现在走这条）

WSL 里装的是 **Linux 版 Isaac Lab**，和官方 `engineai_rl_lab` 的 `.sh` 一致，比在 `C:\Windows\System32` 里敲 bat 靠谱。  
**不会**自动用你 Windows 桌面上的 Isaac；必须在 Ubuntu 里再装一套。

## 0. 先离开 System32（PowerShell 只贴下面 3 行）

```powershell
Set-Location $HOME
wsl --install -d Ubuntu-22.04
```

若提示已安装，跳过 install。然后：

```powershell
wsl
```

看到类似 `user@电脑名:~$` 才算进了 Linux。  
**不要**再贴 `01_setup.bat`、`X:\你的路径`、`REM`。

`git clone` 在 System32 报 `Permission denied` 是正常的：系统目录不能写。家目录可以。

若 `wsl` 不可用：开始菜单搜索 **Ubuntu** 打开。第一次会创建用户名密码。

进 WSL 后确认 GPU：

```bash
cd ~
nvidia-smi
```

这里必须能看到显卡。没有的话先更新 **Windows 上的** NVIDIA 驱动并重启，不要在 WSL 里装 Windows 显卡驱动。

## 1. 克隆本仓库和官方 lab

```bash
cd ~
sudo apt-get update && sudo apt-get install -y git
git clone -b cursor/t800-windows-train-2191 https://github.com/Lakesenberg/Book4_Power-of-Matrix.git
bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/01_clone.sh
```

## 2. 安装 Isaac Lab（只要做一次，很久）

```bash
bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/02_install_isaaclab.sh
```

钉死 Isaac Lab commit `c22775241e28f465fe345fa1a482ad6d29d712b0`，Isaac Sim 5.1。

## 3. 转换动作并开训

```bash
source ~/env_isaaclab/bin/activate
# 16GB 显存:
NUM_ENVS=1024 bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/03_convert_and_train.sh
# 24GB 以上可以默认 2048
```

必须加 `--headless`（脚本里已加）。日志在：

`~/Book4_Power-of-Matrix/t800_stablemimic/vendor/engineai_rl_lab/logs/rsl_rl/tracking_t800/`

## 4. 打包给后续 Linux / 本机续训

```bash
source ~/env_isaaclab/bin/activate
python ~/Book4_Power-of-Matrix/t800_stablemimic/scripts/pack_checkpoints.py \
  --lab-root ~/Book4_Power-of-Matrix/t800_stablemimic/vendor/engineai_rl_lab \
  --out-dir ~/Book4_Power-of-Matrix/t800_stablemimic/handoff_windows_to_linux \
  --stage WIN1_TRACKING
```

## 不要做的事

- 不要在 `C:\Windows\System32` 里 clone / 开 notepad
- 不要把多条命令粘成一行（你之前的 `05_pack_for_linux.batcd $HOME\Documents`）
- 不要用字面量 `X:\你的路径`
- 若在 System32 用 notepad 保存过 `local_config.bat`，到 `C:\Windows\System32` 删掉它（需管理员），以免污染系统目录
