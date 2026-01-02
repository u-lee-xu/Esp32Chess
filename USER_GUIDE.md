# ESP32-P4 国际象棋AI - 使用指南

## 项目简介

这是一个基于TensorFlow Lite Micro的国际象棋AI，部署到ESP32-P4芯片上。项目包含：
- 神经网络评估引擎（CNN架构）
- 完整的走法生成器
- 串口命令界面
- 支持位置评估和最佳走法推荐

---

## 硬件要求

### 必需硬件
- **ESP32-P4开发板**（推荐：WT9932P4-TINY）
- USB数据线（USB-C或Micro-USB，取决于开发板）
- 电脑（Windows 10/11）

### 开发板规格
- 芯片：ESP32-P4 (WT0132P4-A1模组)
- PSRAM：32MB
- Flash：16MB
- USB接口：USB-Serial/JTAG

---

## 软件环境

### 方法1：使用预编译固件（推荐新手）

#### 所需软件
1. **Python**：3.9或更高版本
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **pyserial库**（用于串口通信）
   ```bash
   pip install pyserial
   ```

3. **PuTTY**（可选，用于手动测试）
   - 下载：https://www.putty.org/

#### 使用步骤

1. **下载预编译固件**
   - 从GitHub Releases下载 `esp32_chess_ai.bin`
   - 或自行编译（见下方）

2. **安装esptool烧录工具**
   ```bash
   pip install esptool
   ```

3. **连接开发板**
   - 用USB线连接ESP32-P4到电脑
   - 打开"设备管理器"查看COM端口（如COM19）

4. **烧录固件**
   ```bash
   esptool.py --chip esp32p4 -p COM19 -b 460800 --before=default_reset --after=hard_reset write_flash --flash_mode dio --flash_size 2MB --flash_freq 80m 0x10000 esp32_chess_ai.bin
   ```
   - 将 `COM19` 替换为实际的COM端口

5. **连接串口**
   - 使用PuTTY连接到COM19，波特率115200
   - 或使用Python脚本（见下方）

---

### 方法2：从源码编译（推荐开发者）

#### 所需软件

1. **ESP-IDF工具链**
   - 下载离线安装包：ESP-IDF v5.5.2 Offline Installer
   - 安装到默认路径（或自定义）

2. **Python**：3.9或更高版本
   - ESP-IDF安装程序会自动安装Python虚拟环境

3. **CMake** 和 **Ninja**
   - ESP-IDF安装程序会自动安装

#### 编译步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/u-lee-xu/Esp32Chess.git
   cd Esp32Chess
   ```

2. **设置ESP-IDF环境**
   - 打开ESP-IDF命令提示符（开始菜单 → ESP-IDF 5.5.2）

3. **进入项目目录**
   ```bash
   cd esp32_chess_ai
   ```

4. **配置目标芯片**
   ```bash
   idf.py set-target esp32p4
   ```

5. **编译项目**
   ```bash
   idf.py build
   ```

6. **烧录固件**
   ```bash
   idf.py -p COM19 flash monitor
   ```
   - 将 `COM19` 替换为实际的COM端口

---

## 使用方法

### 方法1：使用Python脚本（推荐）

#### 测试脚本

创建 `test_chess.py`：

```python
import serial
import time

# 配置串口
ser = serial.Serial('COM19', 115200, timeout=30)

# 清空缓冲区
time.sleep(2)
ser.read_all()

print("等待系统启动...")
time.sleep(2)

# 读取启动日志
response = ser.read_all().decode('utf-8', errors='ignore')
print("启动日志:")
print(response)
print("\n" + "="*50 + "\n")

# 测试help命令
print("发送: help")
cmd = "help\n"
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.01)

time.sleep(1)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

# 测试eval命令
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
cmd = f"eval {fen}\n"
print(f"发送: {cmd.strip()}")
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.01)

time.sleep(1)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

# 测试bestmove命令
cmd = f"bestmove {fen}\n"
print(f"发送: {cmd.strip()}")
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.01)

print("等待计算完成（约7秒）...")
time.sleep(8)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

ser.close()
print("\n测试完成")
```

#### 运行测试
```bash
python test_chess.py
```

---

### 方法2：使用PuTTY手动操作

#### 配置PuTTY

1. **基本设置**
   - Serial Line: COM19（根据实际情况修改）
   - Speed: 115200
   - Data bits: 8
   - Stop bits: 1
   - Parity: None
   - Flow control: None

2. **启用本地回显**
   - 左侧导航：Terminal
   - 找到 "Local echo"
   - 设置为 "Force on"

3. **连接**
   - 点击 "Open" 按钮

#### 可用命令

##### 1. help - 显示帮助
```
help
```
或
```
?
```

##### 2. eval - 评估棋盘位置
```
eval <FEN字符串>
```

**示例**：
```
eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

**输出**：
```
Evaluation: 0.000 (均势)
Time: 334.50 ms
```

##### 3. bestmove - 获取最佳走法
```
bestmove <FEN字符串>
```

**示例**：
```
bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

**输出**：
```
Analyzing position...
Best move: e2e4
Time: 7012.79 ms
Depth: 1 (single-ply search)
```

---

## FEN字符串格式说明

FEN（Forsyth-Edwards Notation）是国际象棋棋盘的标准表示法。

### 格式
```
[棋盘布局] [轮到谁走] [王车易位权限] [过路兵] [半回合计数] [回合数]
```

### 示例
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### 字段说明

1. **棋盘布局**：8行棋子，用`/`分隔
   - 大写字母：白方棋子（P=兵, N=马, B=象, R=车, Q=后, K=王）
   - 小写字母：黑方棋子
   - 数字：连续的空格数

2. **轮到谁走**：`w`=白方，`b`=黑方

3. **王车易位权限**：
   - `K`：白方王翼易位
   - `Q`：白方后翼易位
   - `k`：黑方王翼易位
   - `q`：黑方后翼易位
   - `-`：无易位权限

4. **过路兵**：过路兵的目标格（如`e3`），或`-`表示无

5. **半回合计数**：从上次吃子或兵移动开始的回合数

6. **回合数**：当前回合数

---

## 常见问题

### Q1: 找不到COM端口
**A**:
- 确保USB线连接正确
- 检查设备管理器中是否有"USB-Serial/JTAG"设备
- 尝试更换USB线或USB端口

### Q2: 烧录失败
**A**:
- 确保COM端口正确
- 按住开发板的BOOT按钮，然后按RESET按钮
- 尝试降低波特率：`-b 115200`

### Q3: 串口通信乱码
**A**:
- 确认波特率设置为115200
- 在PuTTY中启用Local Echo
- 使用Python脚本代替手动输入

### Q4: bestmove命令无响应
**A**:
- bestmove需要约7秒计算时间，请耐心等待
- 检查FEN字符串是否完整
- 确保没有字符丢失（使用Python脚本）

### Q5: 看门狗警告
**A**:
- 这是正常的警告，不影响功能
- 系统会在计算完成后继续正常工作
- 警告信息：`task_wdt: Task watchdog got triggered`

### Q6: 如何重新烧录固件
**A**:
```bash
idf.py -p COM19 flash monitor
```
或使用esptool：
```bash
esptool.py --chip esp32p4 -p COM19 -b 460800 write_flash 0x10000 esp32_chess_ai.bin
```

---

## 项目结构

```
esp32chess/
├── esp32_chess_ai/          # ESP32项目
│   ├── main/
│   │   ├── chess_ai.cpp     # 主程序
│   │   ├── chess_model.h    # 模型数据
│   │   └── CMakeLists.txt   # 构建配置
│   ├── build/               # 编译输出
│   ├── build.bat            # 编译脚本
│   └── flash.bat            # 烧录脚本
├── models/                  # 模型文件
│   ├── chess_ai_model.keras
│   ├── chess_ai_model.tflite
│   └── chess_model.h
├── test_*.py                # 测试脚本
└── README.md                # 项目说明
```

---

## 性能指标

- **推理时间**：约334ms per position
- **bestmove计算时间**：约7秒（20个走法）
- **模型大小**：639KB (TFLite)
- **Flash使用**：约1MB (99%)
- **PSRAM**：32MB
- **评估准确度**：30%（需要用Stockfish重新训练）

---

## 已知限制

1. **Flash空间紧张**：只剩4%空间，无法增加更多功能
2. **评估准确度低**：仅30%，需要重新训练模型
3. **单层搜索**：bestmove只评估当前走法，无前瞻
4. **看门狗警告**：长时间计算时会触发（不影响功能）

---

## 下一步改进

1. **实现Alpha-Beta搜索**：多层前瞻，提高棋力
2. **使用Stockfish重新训练**：提高评估准确度
3. **优化模型大小**：减少Flash占用
4. **增加WiFi功能**：支持网络对战

---

## 技术支持

- **GitHub仓库**：https://github.com/u-lee-xu/Esp32Chess
- **问题反馈**：在GitHub提交Issue
- **开发板文档**：参考 `WT9932P4-TINY_*.pdf`

---

## 许可证

本项目采用开源许可证，详见LICENSE文件。

---

## 致谢

- ESP-IDF开发团队
- TensorFlow Lite Micro团队
- Stockfish国际象棋引擎
- Lichess对局数据库

---

**最后更新**：2026年1月2日
**版本**：v1.0