# ESP32-P4 Chess AI - 当前状态

## 项目概述
基于TensorFlow Lite Micro的国际象棋AI，部署到ESP32-P4芯片上，支持位置评估和最佳走法推荐。

## 当前状态 (2026-01-03)
- **完成度**: 98%
- **核心功能**: 100%完成
- **稳定性**: 优秀
- **可用性**: 优秀（GUI已完善）

## 已完成功能
✅ 神经网络模型训练（CNN架构）
✅ 模型转换为TFLite格式
✅ ESP32-P4部署成功
✅ 串口命令界面
✅ 位置评估功能（eval命令）
✅ 走法生成器（完整国际象棋规则）
✅ Alpha-Beta搜索算法（1层）
✅ 最佳走法推荐（bestmove命令）
✅ 图形界面（chess_gui.py）
✅ 看门狗系统修复
✅ ESP-NN加速优化
✅ 编译和烧录脚本

## 可用命令
- `help` - 显示帮助信息
- `eval <fen>` - 评估棋盘位置
  - 示例: `eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
  - 返回: 评估值(-1到1)和推理时间（约334ms）
- `bestmove <fen>` - 获取最佳走法
  - 示例: `bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
  - 返回: 最佳走法、计算时间、搜索深度、节点数（约6-8秒）

## 图形界面
- **启动**: `python chess_gui.py`
- **功能**:
  - 完整的8x8棋盘显示
  - 点击走棋操作
  - AI自动对弈模式
  - 实时状态显示
  - AI走法和评分显示
- **使用**:
  1. 运行 `python chess_gui.py`
  2. 等待连接ESP32
  3. 点击"启用AI"按钮
  4. 点击白方棋子走棋
  5. AI自动响应（6-8秒）

## 硬件信息
- 开发板: WT9932P4-TINY (ESP32-P4)
- 串口: USB-Serial/JTAG (COM19)
- 波特率: 115200
- PSRAM: 32MB
- Flash: 16MB

## 编译和烧录
### 方法1: 使用ESP-IDF CMD（推荐）
```batch
# 打开ESP-IDF 5.5.2 CMD
cd C:\Users\Mia\Documents\esp32chess\esp32_chess_ai
rmdir /s /q build
idf.py build
idf.py -p COM19 flash monitor
```

### 方法2: 使用rebuild_flash.bat
```batch
cd C:\Users\Mia\Documents\esp32chess\esp32_chess_ai
rebuild_flash.bat
```

## 重要注意事项

### 1. 串口输入时序要求
**问题**: 快速发送字符会导致字符丢失
**解决**: 发送命令时，每个字符之间需要5-10ms延迟，或使用复制粘贴

**Python示例**:
```python
ser = serial.Serial('COM19', 115200, timeout=10)
cmd = "help\n"
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.01)  # 10ms延迟
```

### 2. Flash空间紧张
- 固件大小: 998KB
- 分区大小: 1MB
- 剩余空间: 5%
- 建议: 不要再增加模型大小

### 3. 看门狗系统
- 已正确初始化
- 无警告，系统稳定
- 超时时间: 5秒
- 在长时间计算中自动喂狗

### 4. bestmove命令计算时间
- 计算时间: 6-8秒
- 搜索深度: 1层（Alpha-Beta搜索）
- 节点评估: 约20个
- 请耐心等待，不要中断

### 5. GUI使用说明
- 确保ESP32已连接到COM19
- 关闭其他占用COM19的程序
- AI思考时不要关闭GUI
- 如遇连接问题，重启GUI程序

## 待改进功能
⏳ 模型评估准确度提升（使用Stockfish重新训练）
⏳ 模型大小优化（减少Flash占用）
⏳ 搜索深度优化（增加深度或迭代加深）

## 性能指标
- 神经网络推理时间: ~334ms
- bestmove计算时间: ~6-8秒
- 搜索深度: 1层（Alpha-Beta搜索）
- 节点评估: 约20个
- Tensor Arena使用: 512KB / 32MB PSRAM
- 模型大小: 639KB (TFLite)
- 评估准确度: 30%（需要用Stockfish重新训练）
- Flash使用: 998KB / 1MB (99%)

## 文件结构
```
esp32chess/
├── esp32_chess_ai/          # ESP32项目
│   ├── main/
│   │   ├── chess_ai.cpp     # 主程序（含走法生成和Alpha-Beta搜索）
│   │   ├── chess_model.h    # 模型数据
│   │   └── CMakeLists.txt   # 构建配置（启用ESP-NN）
│   ├── build/               # 编译输出
│   ├── rebuild_flash.bat    # 编译烧录脚本
│   └── README.md            # 项目说明
├── models/                  # 模型文件
│   ├── chess_ai_model.keras
│   ├── chess_ai_model.tflite
│   └── chess_model.h
├── chess_gui.py             # 图形界面（Tkinter）
├── chess_ai_simple.py       # 简单示例脚本
├── PROJECT_LOG.md           # 详细项目记录
├── README_CURRENT_STATUS.md # 本文件
└── USER_GUIDE.md            # 使用指南
```

## 测试脚本
- `test_watchdog.py` - 测试看门狗（推荐）
- `test_normal.py` - 测试正常功能
- `test_slow.py` - 慢速发送测试

## 下一步计划
1. 使用Stockfish重新训练模型（提高准确度）
2. 优化模型大小（减少Flash占用）
3. 增加搜索深度或实现迭代加深

## Git状态
- 本地提交: 已完成
- 远程推送: 待完成（网络问题）
- 分支: main

## 常见问题

### Q: 为什么串口输入会丢失字符？
A: USB-Serial/JTAG接口的时序限制，需要在字符间添加5-10ms延迟，或使用复制粘贴。

### Q: bestmove命令为什么需要6-8秒？
A: 需要进行1层Alpha-Beta搜索，评估约20个节点，每个节点需要334ms推理时间。

### Q: 如何使用图形界面？
A: 运行 `python chess_gui.py`，点击"启用AI"按钮，然后点击棋子走棋即可。

### Q: 如何测试功能？
A: 运行 `test_esp32_bestmove.py` 脚本，它会发送测试命令并验证响应。

### Q: 编译时找不到idf.py？
A: 请使用ESP-IDF 5.5.2 CMD，而不是普通CMD或PowerShell。

### Q: 看门狗警告是什么？
A: 已修复，使用新版本的ESP-IDF API正确初始化看门狗系统，并在长时间计算中自动处理。

### Q: GUI无法连接ESP32？
A: 确保ESP32已连接到COM19，关闭其他占用COM19的程序（如PuTTY），重启GUI程序。

## 联系信息
- 项目仓库: https://github.com/u-lee-xu/Esp32Chess
- 最后更新: 2026年1月3日
- 当前版本: v1.1

---
**注意**: 如果明天继续开发，请先阅读PROJECT_LOG.md的完整历史记录。