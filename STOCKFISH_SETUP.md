# Stockfish 安装指南

## 什么是Stockfish？

Stockfish是最强大的开源国际象棋引擎之一，评估水平超过人类特级大师。我们将用它来为棋局位置生成高质量的评估值。

## 安装步骤

### Windows

#### 方法1：下载预编译版本（推荐）

1. **下载Stockfish**
   - 访问：https://stockfishchess.org/download
   - 选择 "Windows" 版本
   - 下载最新版本（如 stockfish-16-win.zip）

2. **解压文件**
   - 解压到任意目录（如 `C:\Stockfish\`）
   - 记住解压路径

3. **添加到PATH（可选）**
   - 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
   - 在"系统变量"中找到"Path"，点击"编辑"
   - 点击"新建"，添加Stockfish解压目录（如 `C:\Stockfish\`）
   - 点击"确定"保存

4. **验证安装**
   ```powershell
   stockfish --version
   ```
   应该显示类似：`Stockfish 16 by the Stockfish developers`

#### 方法2：不添加到PATH（简单）

如果不想修改PATH，可以修改脚本指定Stockfish路径：

```python
# 在 generate_evaluations.py 中修改
evaluator = StockfishEvaluator(stockfish_path="C:\\Stockfish\\stockfish-windows-x86-64-avx2.exe")
```

### Linux/Mac

```bash
# 下载
wget https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-16-linux-x86-64.tar.bz2

# 解压
tar -xjf stockfish-16-linux-x86-64.tar.bz2

# 添加执行权限
chmod +x stockfish-16-linux-x86-64-avx2

# 移动到PATH
sudo mv stockfish-16-linux-x86-64-avx2 /usr/local/bin/stockfish

# 验证
stockfish --version
```

## 使用方法

### 1. 生成评估值

```bash
python generate_evaluations.py
```

这个脚本会：
- 读取PGN文件
- 用Stockfish评估每个位置
- 生成带评估值的训练数据

**注意**：评估速度取决于：
- Stockfish深度（默认15）
- CPU性能
- 位置数量

**预计时间**：
- 100局 × 30位置 = 3000个位置
- 每个位置约1-2秒
- 总计约1-2小时

### 2. 调整评估参数

编辑 `generate_evaluations.py`：

```python
# 修改评估深度（15-20之间）
self.depth = 15  # 更快，质量略低
self.depth = 20  # 更慢，质量更高

# 修改处理的游戏数量
process_pgn_file(
    pgn_file,
    output_file,
    max_games=500,  # 增加到500局
    max_positions_per_game=50  # 每局50个位置
)
```

### 3. 重新训练模型

生成评估值后：

```bash
# 修改 train_model.py 使用新文件
# 将 data_file 改为 "chess_training_data_with_eval.json"

python train_model.py
```

## 性能优化

### 1. 减少评估深度

如果太慢，降低深度：

```python
self.depth = 10  # 更快（约0.5秒/位置）
```

### 2. 减少位置数量

```python
max_positions_per_game=20  # 从30减少到20
```

### 3. 使用多进程（高级）

可以修改脚本使用多进程并行评估（需要修改代码）

## 常见问题

### Q: Stockfish启动失败
A: 检查：
1. Stockfish是否正确安装
2. 路径是否正确
3. 是否有执行权限（Linux/Mac）

### Q: 评估速度太慢
A:
1. 降低评估深度（15 → 10）
2. 减少处理的游戏数量
3. 使用更快的CPU

### Q: 内存不足
A:
1. 减少max_positions_per_game
2. 分批处理游戏

## 下一步

1. 安装Stockfish
2. 运行 `python generate_evaluations.py`
3. 等待评估完成
4. 用新数据重新训练模型

## 参考资料

- Stockfish官网：https://stockfishchess.org/
- GitHub仓库：https://github.com/official-stockfish/Stockfish
- UCI协议文档：https://www.shredderchess.com/chess-info/features/uci-universal-chess-interface.html