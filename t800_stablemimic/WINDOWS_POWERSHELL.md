# 你刚才那串报错的原因

PowerShell 当时在 **`C:\Windows\System32`**（系统目录）。  
`t800_stablemimic` **不在**这里，所以 `cd` 失败；后面的 `01_setup.bat`、`REM` 才会全部找不到。

另外：

- PowerShell 里跑当前目录的 bat，必须写成 **`.\01_setup.bat`**，不能只写 `01_setup.bat`
- **`REM` 是 cmd 注释**，PowerShell 里用 `#`

# 正确顺序（复制整段）

先确认本机已装 [Git](https://git-scm.com/download/win)。然后**不要**停在 System32：

```powershell
# 1. 离开系统目录，去用户文档
cd $HOME\Documents

# 2. 拉带训练脚本的分支（还没有仓库时）
git clone -b cursor/t800-windows-train-2191 https://github.com/Lakesenberg/Book4_Power-of-Matrix.git
cd Book4_Power-of-Matrix\t800_stablemimic

# 3. 启动检查（会 clone 官方 engineai_rl_lab）
powershell -ExecutionPolicy Bypass -File .\Start-Here.ps1
```

如果 **Book4 已经克隆过**（在别的盘）：

```powershell
cd X:\你的路径\Book4_Power-of-Matrix
git fetch origin
git checkout cursor/t800-windows-train-2191
cd t800_stablemimic
powershell -ExecutionPolicy Bypass -File .\Start-Here.ps1
```

然后仍在 `t800_stablemimic\windows` 里：

```powershell
cd .\windows
notepad .\local_config.bat
# 改 ISAAC_PYTHON 为 Isaac Lab 环境的 python；16GB 显存把 NUM_ENVS 改成 1024

.\02_convert_motion.bat
.\03_train_stage0_tracking.bat
.\05_pack_for_linux.bat
```

用资源管理器确认这个文件存在再跑：

`Documents\Book4_Power-of-Matrix\t800_stablemimic\windows\01_setup.bat`

# 怎样知道走对了

`Start-Here.ps1` / `01_setup.bat` 成功时会打印：

- `[OK] 已存在 ...\engineai_rl_lab` 或正在 clone
- 下一步去改 `local_config.bat`、跑 `02_convert_motion.bat`

若仍提示找不到路径，把 `Get-Location` 和 `dir` 的输出发过来。
