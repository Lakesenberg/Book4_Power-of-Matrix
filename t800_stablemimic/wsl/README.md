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

## 0.5 若 `set: pipefail` / Release file is not valid yet

脚本报 `set: pipefail` 是 Windows 换行（CRLF）。仓库已改成 LF。你**现在这台**先修本地文件，不必等 pull：

```bash
sed -i 's/\r$//' ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/*.sh
sed -i 's/\r$//' ~/Book4_Power-of-Matrix/t800_stablemimic/linux/*.sh
```

`apt` 报 `Release file is not valid yet` 是 WSL 时钟慢了。`hwclock` 在许多 WSL 里不存在，不必装。安装脚本已改为跳过 Release 日期。

你也可以在 **Windows PowerShell**（先 `Set-Location $HOME`）执行一次：

```powershell
wsl --shutdown
```

再重新打开 Ubuntu，时钟常会对齐。

`(base)` 是 conda。Ubuntu Resolute 往往没有 `python3.11` 软件包，脚本会改用 `conda create -n isaaclab python=3.11`。不要用 conda base 装 Isaac。

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

## 4. 静态扭曲起身（跟舞跑完后）

```bash
conda activate isaaclab
NUM_ENVS=64 bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/04_train_getup.sh
```

不转 csv、不用 `dance_t800.npz`。日志在 `logs/rsl_rl/getup_t800/`。详见 [../getup/README.md](../getup/README.md)。

## 5. 打包给后续 Linux / 本机续训

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
