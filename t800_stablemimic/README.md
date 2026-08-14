# T800：Windows 先训 tracking，Linux 再接起身

当前云环境没有 GPU，**Isaac Sim 训练要在你的 Windows 机器上跑**。  
这里是官方 `engineai_rl_lab` 的一键脚本：Windows 只做能单卡跑的 tracking，再把指定 checkpoint 拿到 Linux 做 StableMimic / 扭曲起身。

## Windows（现在就做）

**不要在 `C:\Windows\System32` 里跑这些命令。**  
你现在这种环境请改走 **WSL Ubuntu 里装 Linux 版 Isaac Lab**：见 [wsl/README.md](wsl/README.md)。  
原生 PowerShell/bat 步骤见 [WINDOWS_POWERSHELL.md](WINDOWS_POWERSHELL.md)。

1. 安装 [Isaac Lab 2.3.2](https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/installation/index.html) + Isaac Sim 5.1（Win11，钉死 commit `c22775241e28f465fe345fa1a482ad6d29d712b0`）。  
2. 开启长路径；显存 16GB 把 `NUM_ENVS` 设为 1024。  
3. 在 **仓库里的** `t800_stablemimic\windows` 运行（PowerShell 必须加 `.\`）：

```powershell
cd $HOME\Documents
git clone -b cursor/t800-windows-train-2191 https://github.com/Lakesenberg/Book4_Power-of-Matrix.git
cd Book4_Power-of-Matrix\t800_stablemimic
powershell -ExecutionPolicy Bypass -File .\Start-Here.ps1
cd .\windows
# 用记事本改 local_config.bat 里的 ISAAC_PYTHON
.\02_convert_motion.bat
.\03_train_stage0_tracking.bat
.\05_pack_for_linux.bat
```

中途断了用 `.\03b_resume_tracking.bat`。看效果用 `.\04_play_check.bat`（先 `$env:LOAD_RUN="..."`）。

产物：`t800_stablemimic/handoff_windows_to_linux/`。

## 拿到 Linux 的东西

见 [CHECKPOINT_HANDOFF.md](CHECKPOINT_HANDOFF.md)。核心就是：

- `logs/rsl_rl/tracking_t800/<run>/model_<N>.pt`  
- 同目录 `params/`  
- `datasets/tracking/t800/dance_t800.npz`  
- `handoff/manifest.json`

## Linux（下一步）

```bash
cd engineai_rl_lab
../t800_stablemimic/linux/01_unpack_and_resume.sh /path/to/handoff_windows_to_linux
# 可选：按 manifest 里的 linux_resume_cmd 升到 4096 继续 tracking
# get-up 库齐了再：
../t800_stablemimic/linux/02_train_stablemimic_lite.sh
```

官方仓库目前只有 tracking 任务。LIN2/LIN3 要等 `Tracking-StableMimic-T800-v0` 合入；**Windows 这份 `model_*.pt` 就是初始化权重，先训起来不必等。**
