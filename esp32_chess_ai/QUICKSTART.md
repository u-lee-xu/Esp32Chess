# ESP32-P4 Chess AI - 快速开始

## 前提条件

- ✅ ESP-IDF v5.5.2 已下载到 `C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2`
- ✅ 项目文件已准备
- ⏳ ESP32-P4 开发板
- ⏳ USB 数据线

## 编译步骤

### 1. 编译项目

双击运行 `build.bat`，或在PowerShell中执行：

```powershell
cd C:\Users\Mia\Documents\esp32chess\esp32_chess_ai
.\build.bat
```

这个脚本会：
- 设置ESP-IDF环境变量
- 设置目标芯片为ESP32-P4
- 编译项目

**预计时间**：5-10分钟（首次编译）

### 2. 连接ESP32-P4

1. 用USB数据线连接ESP32-P4到电脑
2. 打开"设备管理器"查看COM端口
   - Win + X → 设备管理器
   - 端口(COM和LPT) → 查找类似"USB Serial Port (COM3)"

### 3. 烧录固件

双击运行 `flash.bat`，或在PowerShell中执行：

```powershell
.\flash.bat
```

输入COM端口（如 `COM3`），按回车。

**预计时间**：1-2分钟

### 4. 查看串口输出

烧录完成后，可以选择启动串口监视器：

```powershell
idf.py -p COM3 monitor
```

或使用其他串口工具（如PuTTY、TeraTerm）：
- 波特率：115200
- 数据位：8
- 停止位：1
- 校验位：无

## 使用方法

### 串口命令

连接成功后，你会看到：

```
****************************************
*      ESP32-P4 Chess AI v1.0         *
*      Neural Network Evaluator       *
****************************************

Model: chess_ai_model.tflite (639KB)
Input: 8x8x12 board tensor
Output: Position evaluation (-1 to 1)
Parameters: 158,753
Tensor Arena: 512KB / 32MB PSRAM

Type 'help' for available commands.

>
```

### 可用命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `eval <fen>` | 评估棋盘位置 | `eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` |
| `bestmove <fen>` | 获取最佳走法 | `bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` |
| `help` | 显示帮助 | `help` |

### 示例会话

```
> eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

Evaluation: 0.0095 (均势)
Time: 334.50 ms

> eval r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3

Evaluation: 0.0319 (均势)
Time: 332.15 ms

> help

========================================
        ESP32-P4 Chess AI Commands
========================================

eval <fen>       - Evaluate a chess position
bestmove <fen>   - Get the best move for a position
help             - Show this help message
?                - Show this help message

========================================

>
```

## 常见问题

### Q: 编译失败
A:
1. 检查ESP-IDF路径是否正确
2. 确保Python 3.8+已安装
3. 运行 `idf.py fullclean` 后重新编译

### Q: 烧录失败
A:
1. 确认ESP32-P4已连接
2. 检查COM端口是否正确
3. 按住ESP32-P4的BOOT按钮，再按RESET按钮进入下载模式

### Q: 串口无输出
A:
1. 检查波特率是否为115200
2. 确认COM端口正确
3. 按ESP32-P4的RESET按钮重启

### Q: 评估结果异常
A:
1. 检查FEN格式是否正确
2. 确认模型文件已正确编译
3. 查看ESP32日志输出

## 性能数据

- **推理时间**：~334ms（位置评估）
- **bestmove计算时间**：~6-8秒（1层搜索，约20个节点）
- **搜索深度**：1层
- **内存占用**：约512KB（Tensor Arena）
- **模型大小**：639KB（纯float32）
- **CPU频率**：400MHz
- **ESP-NN优化**：已启用（提升30-50%）

## 下一步

1. 测试基本功能
2. 尝试评估不同的棋局位置
3. （可选）添加走法生成器
4. （可选）添加Alpha-Beta搜索

## 参考资料

- [ESP32-P4 技术参考手册](https://www.espressif.com/sites/default/files/documentation/esp32-p4_technical_reference_manual_cn.pdf)
- [ESP-IDF 编程指南](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32p4/)
- [TensorFlow Lite for Microcontrollers](https://www.tensorflow.org/lite/microcontrollers)