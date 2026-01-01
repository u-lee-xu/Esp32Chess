# 串口命令使用说明

## 连接ESP32-P4

使用USB数据线连接ESP32-P4开发板到电脑。

## 打开串口终端

### Windows
- 使用PuTTY、TeraTerm或Arduino IDE的串口监视器
- 波特率：115200
- 数据位：8
- 停止位：1
- 校验位：无

### Linux/Mac
```bash
# 查找串口设备
ls /dev/ttyUSB*

# 使用minicom或screen
screen /dev/ttyUSB0 115200
```

## 可用命令

### 1. eval - 评估棋盘位置

评估给定的FEN格式棋局，返回位置评分。

**语法**：
```
eval <fen>
```

**示例**：
```
> eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

Evaluation: 0.05 (均势)
Time: 12.5 ms
```

**评分说明**：
- `> 0.3`：白方优势
- `< -0.3`：黑方优势
- `-0.3 ~ 0.3`：均势
- `1.0`：白方必胜
- `-1.0`：黑方必胜

### 2. bestmove - 获取最佳走法

分析位置并建议最佳走法（当前版本仅返回评估值）。

**语法**：
```
bestmove <fen>
```

**示例**：
```
> bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

Analyzing position...
Result: eval:0.05

Note: Full move generation not implemented yet.
This feature requires move generator and Alpha-Beta search.
```

### 3. help - 显示帮助信息

显示所有可用命令和使用说明。

**语法**：
```
help
```

或

```
?
```

**示例**：
```
> help

========================================
        ESP32-P4 Chess AI Commands
========================================

eval <fen>       - Evaluate a chess position
                  Example: eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

bestmove <fen>   - Get the best move for a position
                  Example: bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

help             - Show this help message
?                - Show this help message

========================================
```

## 常用FEN示例

### 起始位置
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### 意大利开局
```
r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3
```

### 西西里防御
```
rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2
```

### 王翼弃兵
```
rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2
```

### 后翼弃兵
```
rnbqkbnr/pp1ppppp/8/2p5/8/2PP4/PP2PPPP/RNBQKBNR w KQkq c6 0 2
```

### 中局复杂局面
```
r4rk1/pp2ppbp/2p3p1/8/2BP2n1/2N1P3/PP3PPP/R3KB1R w KQ - 0 12
```

## 使用技巧

1. **输入FEN时可以省略后面的信息**：
   ```
   eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR
   ```

2. **使用退格键删除字符**：
   ```
   > eva<退格>l rnbqkbnr/...
   ```

3. **多次评估比较不同局面**：
   ```
   > eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
   Evaluation: 0.05 (均势)

   > eval r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3
   Evaluation: 0.12 (白方优势)
   ```

## 性能数据

- **推理时间**：10-20ms
- **内存占用**：约200KB
- **模型大小**：170KB

## 故障排查

### 无法输入命令
- 检查串口连接
- 确认波特率设置为115200
- 尝试重新烧录固件

### 评估结果异常
- 检查FEN格式是否正确
- 确保模型文件正确加载
- 查看ESP32日志输出

### 响应缓慢
- 检查ESP32-P4 CPU频率
- 确认没有其他高优先级任务占用CPU
- 考虑优化TensorFlow Lite配置