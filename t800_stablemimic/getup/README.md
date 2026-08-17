# T800 静态扭曲起身

官方 `engineai_rl_lab` 只有跟舞。这里加任务 **`Getup-Twisted-T800-v0`**：从地面静态扭曲位姿尽快站稳。

- **不用** `dance_t800.npz`
- **不用** 推倒 / 舞中摔倒
- **不从** tracking 的 `model_19999.pt` 热启动（观测不同，load 会对不上）

## 位姿课程

| 阶段 | 采样 | 目的 |
|------|------|------|
| 0 | 坐靠 + 仰卧 | 先学会快站起来 |
| 1 | 仰卧 | 打牢仰躺起身 |
| 2 | 仰卧 + 左/右侧卧 | 再加侧身 |
| 3 | 再加俯卧 | 俯仰分开，避免一开始互扰 |
| 4 | 再加交叉腿 / 躯干扭转 | |
| 5 | 再加手臂压在身下 | 最难发力 |

每个 episode 开始时机器人已经躺在地上，关节和朝向带噪声，速度为 0。成功标准：高度、直立、水平速度都达标并保持约 0.6s。站得越早奖励越高。

## WSL（你现在这台）

先 `git pull` 本仓库，再：

```bash
conda activate isaaclab
# PhysX 若仍掉 CPU，先用 64，通了再 128
NUM_ENVS=64 bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/04_train_getup.sh
```

日志：`vendor/engineai_rl_lab/logs/rsl_rl/getup_t800/`

回放：

```bash
# 有窗口
bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/05_play_getup.sh
# 无窗口
HEADLESS=1 bash ~/Book4_Power-of-Matrix/t800_stablemimic/wsl/05_play_getup.sh
```

## 怎样算这阶段够了

- 有 `model_8000.pt` 以上
- TensorBoard 里 `standing` / `fast_stand` 上升，`Episode_Length` 变长
- 回放能从仰卧在 2–3 秒内站稳；侧卧/交叉也会试着起来

默认 15000 iteration，约每 1000 轮存盘。