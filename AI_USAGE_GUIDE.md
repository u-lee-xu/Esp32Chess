# ESP32国际象棋AI使用指南

## 快速开始

### 1. 连接ESP32

```bash
python chess_ai_simple.py
```

这个脚本展示了基本用法：
- 连接ESP32串口（COM19）
- 评估棋盘位置
- 获取最佳走法

### 2. 交互式调试

```bash
python chess_ai_interactive.py
```

提供交互式命令行界面，可以：
- 输入任意FEN字符串
- 实时查看AI评估
- 获取最佳走法建议
- 查看棋盘可视化

## 工作原理

### 输入：FEN格式

ESP32接受**FEN (Forsyth-Edwards Notation)**格式的棋盘状态：

```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

**格式解释**：

| 位置 | 内容 | 说明 |
|------|------|------|
| 1 | `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR` | 棋盘布局（8行） |
| 2 | `w` | 轮到白方走 |
| 3 | `KQkq` | 王车易位权限 |
| 4 | `-` | 过路兵目标格 |
| 5 | `0` | 半回合计数 |
| 6 | `1` | 回合数 |

**棋子编码**：
- 大写字母：白方（P=兵, N=马, B=象, R=车, Q=后, K=王）
- 小写字母：黑方（p=兵, n=马, b=象, r=车, q=后, k=王）
- 数字：连续空格数（8=8个空格）

### 输出：评估和走法

#### 1. 评估命令 (`eval`)

**输入**：
```
eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

**输出**：
```
Evaluation: 0.0123
Time: 334ms
```

**评估值范围**：
- `+1.0`：白方巨大优势
- `+0.5`：白方略优
- `0.0`：均势
- `-0.5`：黑方略优
- `-1.0`：黑方巨大优势

#### 2. 最佳走法命令 (`bestmove`)

**输入**：
```
bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

**输出**：
```
Best move: e2e4
Evaluation: +0.15
Time: 7.2s
Depth: 1 (single-ply search)
Nodes: 20
```

**走法格式** (UCI)：
- `e2e4`：从e2移动到e4
- `e7e8q`：从e7移动到e8，升变为后

## 集成到实际下棋程序

### Python示例

```python
import serial
import time

class ChessAI:
    def __init__(self, port='COM19'):
        self.ser = serial.Serial(port, 115200, timeout=30)
        time.sleep(2)
        self.ser.read_all()

    def get_best_move(self, fen):
        """获取最佳走法"""
        # 发送命令
        for char in f"bestmove {fen}":
            self.ser.write(char.encode())
            time.sleep(0.01)
        self.ser.write(b'\n')

        # 等待响应
        time.sleep(15)
        response = self.ser.read_all().decode('utf-8')

        # 解析走法
        if "Best move:" in response:
            move = response.split("Best move:")[1].split()[0]
            return move
        return None

# 使用示例
ai = ChessAI()

# 当前棋盘（FEN格式）
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# 获取AI建议
best_move = ai.get_best_move(fen)
print(f"AI建议: {best_move}")  # 输出: e2e4
```

### JavaScript示例（Web应用）

```javascript
const SerialPort = require('serialport');
const Readline = require('@serialport/parser-readline');

async function getBestMove(fen) {
    const port = new SerialPort({ path: 'COM19', baudRate: 115200 });
    const parser = port.pipe(new Readline({ delimiter: '\n' }));

    // 发送命令
    port.write(`bestmove ${fen}\n`);

    // 等待响应
    return new Promise((resolve) => {
        parser.on('data', (data) => {
            if (data.includes('Best move:')) {
                const move = data.split('Best move:')[1].trim().split()[0];
                port.close();
                resolve(move);
            }
        });
    });
}

// 使用
getBestMove('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    .then(move => console.log('AI建议:', move));
```

## 完整对局流程

```
1. 初始化棋盘
   ↓
2. 轮到白方（玩家）
   ↓
3. 玩家输入走法（例如：e2e4）
   ↓
4. 更新棋盘
   ↓
5. 轮到黑方（AI）
   ↓
6. 将棋盘转换为FEN
   ↓
7. 发送FEN到ESP32
   ↓
8. ESP32计算最佳走法（5-10秒）
   ↓
9. 返回最佳走法（例如：e7e5）
   ↓
10. 更新棋盘
    ↓
11. 回到步骤2，直到游戏结束
```

## 常见FEN示例

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

## 性能参数

- **推理时间**：~334ms（位置评估）
- **计算时间**：6-8秒（最佳走法，1层搜索）
- **搜索深度**：1层
- **评估节点**：约20个
- **ESP-NN优化**：已启用（提升30-50%）

## 注意事项

1. **串口延迟**：发送命令时每个字符间需要10ms延迟
2. **计算时间**：bestmove命令需要5-10秒，请耐心等待
3. **FEN格式**：确保FEN字符串格式正确
4. **轮次信息**：FEN中的轮次信息（w/b）必须正确

## 故障排除

### 问题：字符丢失
**解决**：增加字符间延迟到10-15ms

### 问题：无响应
**解决**：
1. 检查串口连接
2. 检查波特率（115200）
3. 增加超时时间

### 问题：评估值异常
**解决**：检查FEN格式是否正确

## 相关文件

- `chess_ai_simple.py` - 简单使用示例
- `chess_ai_interactive.py` - 交互式调试工具
- `test_watchdog.py` - 系统测试脚本

## 下一步

1. 烧录固件到ESP32
2. 运行`chess_ai_simple.py`测试
3. 集成到您的下棋程序
4. 享受与AI对弈！