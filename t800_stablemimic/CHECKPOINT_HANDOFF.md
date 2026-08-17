# 从 Windows 带到 Linux 的 checkpoint

Windows 只训官方 T800 **whole-body tracking**（单卡、Isaac Lab）。  
摔倒起身 / 扭曲姿势 / 双专家 MoE / Sim2Sim / 真机，都在 Linux 用 **同一套权重接着训**。

## 必须拷走的文件

打包脚本 `windows/05_pack_for_linux.bat` 会生成 `t800_stablemimic/handoff_windows_to_linux/`。  
把**整个目录**拷到 Linux，用 `linux/01_unpack_and_resume.sh` 合并进 `engineai_rl_lab`。

| 路径（相对 `engineai_rl_lab`） | 为什么要 |
|--------------------------------|----------|
| `logs/rsl_rl/tracking_t800/<run>/model_<N>.pt` | **主权重**。Linux `runner.load()` / `--checkpoint` 用这个 |
| `logs/rsl_rl/tracking_t800/<run>/params/env.yaml` | 环境超参，resume 对齐 |
| `logs/rsl_rl/tracking_t800/<run>/params/agent.yaml` | PPO / 网络结构，必须与 Windows 一致才能 load |
| `logs/rsl_rl/tracking_t800/<run>/params/env.pkl` | 有则带上 |
| `logs/rsl_rl/tracking_t800/<run>/params/agent.pkl` | 有则带上 |
| `datasets/tracking/t800/dance_t800.npz` | 训练用参考动作（和 Windows 必须同一份） |
| `datasets/tracking/t800/dance_t800.csv` | 源数据，Linux 可重转 npz |
| `handoff/manifest.json` | run 名、iteration、续训命令 |

`<run>` 形如 `2026-08-14_15-03-11_win1_tracking`。  
`<N>` 取**最大**的那个（官方 `save_interval=2000`，训满是 `model_20000.pt`）。中途停了就带最新的，例如 `model_8000.pt`。

`manifest.json` 里的 `checkpoint_name` / `run_name` / `linux_resume_cmd` 以打包时为准，不要猜。

## 不要拷

- Isaac Sim / Isaac Lab 安装目录  
- `videos/`、`wandb/`、`logs/rsl_rl/temp/`  
- 虚拟环境、CUDA、驱动  
- 还没训出来的 get-up / MoE 权重（Linux 才有）

ONNX / MNN 可选。Windows 若没跑 `play.py` 导出，到 Linux 再导即可。

## Linux 接到哪一步

1. **LIN1**（可选）：同一任务升到 `--num_envs 4096` 继续 tracking  
   ```bash
   python scripts/tracking/train.py \
     --task Tracking-Flat-T800-Wo-State-Estimation-v0 \
     --headless --num_envs 4096 \
     --motion_file datasets/tracking/t800/dance_t800.npz \
     --resume True \
     --load_run <manifest.run_name> \
     --checkpoint <manifest.checkpoint_name>
   ```
2. **GETUP1 / LIN2**：新任务 `Getup-Twisted-T800-v0`（静态扭曲躺姿课程，尽快站稳）。**不要**拿 tracking 的 pt `--resume`，观测维不同。  
3. **LIN3**（可选）：只有还要「跳舞 + 被推 + 再跳」时才做 MoE。  
4. **LIN4**：`play.py` 导出，进 `native_sdk`。

观测/动作维必须和 Windows tracking 一致，否则 `load` 会因 shape 对不上失败。不要换 `Tracking-Flat-T800-Wo-State-Estimation-v0` 的 policy 项顺序。

## 怎样算 Windows 阶段够了

可以停 WIN1、去打包的信号：

- 已有 `model_*.pt`（最好 ≥ `model_10000.pt`，理想 `model_20000.pt`）  
- TensorBoard 上 tracking 误差开始平台，episode 不再秒切  
- `04_play_check.bat` 能跟完一段舞、不乱甩肢  

没收敛也可以先打包：Linux 用同一 pt `--resume True` 接着训即可。
