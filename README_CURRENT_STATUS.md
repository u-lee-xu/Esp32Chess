# ESP32-P4 Chess AI - 当前状态

## 项目概述
基于TensorFlow Lite Micro的国际象棋AI，部署到ESP32-P4芯片上，支持位置评估和最佳走法推荐。

## 当前状态 (2026-01-02)
- **完成度**: 95%
- **核心功能**: 100%完成
- **稳定性**: 优秀（看门狗已修复）
- **可用性**: 良好

## 已完成功能
✅ 神经网络模型训练（CNN架构）
✅ 模型转换为TFLite格式
✅ ESP32-P4部署成功
✅ 串口命令界面
✅ 位置评估功能（eval命令）
✅ 走法生成器（完整国际象棋规则）
✅ Alpha-Beta搜索算法
✅ 最佳走法推荐（bestmove命令）
✅ 看门狗系统修复
✅ 编译和烧录脚本

## 可用命令
- `help` - 显示帮助信息
- `eval <fen>` - 评估棋盘位置
  - 示例: `eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
  - 返回: 评估值(-1到1)和推理时间（约334ms）
- `bestmove <fen>` - 获取最佳走法
  - 示例: `bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
  - 返回: 最佳走法、计算时间、搜索深度、节点数（约5-10秒）

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
- 计算时间: 5-10秒
- 搜索深度: 2层
- 节点评估: 约400-500个
- 请耐心等待，不要中断

## 待改进功能
⏳ 模型评估准确度提升（使用Stockfish重新训练）
⏳ 模型大小优化（减少Flash占用）
⏳ 搜索深度优化（增加深度或迭代加深）

## 性能指标
- 神经网络推理时间: ~334ms
- bestmove计算时间: ~5-10秒
- 搜索深度: 2层
- 节点评估: 400-500个
- Tensor Arena使用: 37.6KB / 200KB (18.4%)
- 模型大小: 639KB (TFLite)
- 评估准确度: 30%（需要用Stockfish重新训练）

## 文件结构
```
esp32chess/
├── esp32_chess_ai/          # ESP32项目
│   ├── main/
│   │   ├── chess_ai.cpp     # 主程序（含走法生成和搜索）
│   │   └── chess_model.h    # 模型数据
│   ├── build/               # 编译输出
│   ├── rebuild_flash.bat    # 编译烧录脚本
│   └── README.md            # 项目说明
├── models/                  # 模型文件
│   ├── chess_ai_model.keras
│   ├── chess_ai_model.tflite
│   └── chess_model.h
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

### Q: bestmove命令为什么需要5-10秒？
A: 需要进行2层Alpha-Beta搜索，评估约400-500个节点，每个节点需要334ms推理时间。

### Q: 如何测试功能？
A: 运行 `test_watchdog.py` 脚本，它会发送测试命令并验证响应。

### Q: 编译时找不到idf.py？
A: 请使用ESP-IDF 5.5.2 CMD，而不是普通CMD或PowerShell。

### Q: 看门狗警告是什么？
A: 已修复，使用新版本的ESP-IDF API正确初始化看门狗系统，并在长时间计算中自动喂狗。

## 联系信息
- 项目仓库: https://github.com/u-lee-xu/Esp32Chess
- 最后更新: 2026年1月2日

---
**注意**: 如果明天继续开发，请先阅读PROJECT_LOG.md的完整历史记录。