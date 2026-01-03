# ESP32-P4 Chess AI

基于TensorFlow Lite Micro的国际象棋AI，部署到ESP32-P4芯片，支持位置评估、走法生成和最佳走法推荐。

## 硬件要求

- ESP32-P4开发板（推荐：WT9932P4-TINY）
- USB数据线

## 软件要求

- ESP-IDF v5.5.2
- Python 3.9+
- CMake 3.16+

## 编译步骤

### 1. 安装ESP-IDF

```bash
# 克隆ESP-IDF仓库
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
git checkout v5.5.2
git submodule update --init --recursive

# 安装依赖
./install.sh esp32p4

# 设置环境变量
. ./export.sh
```

### 2. 编译项目

```bash
cd esp32_chess_ai
idf.py set-target esp32p4
idf.py build
```

### 3. 烧录到开发板

```bash
# 连接开发板后
idf.py -p COM19 flash monitor
```

## 功能说明

### 当前实现

- ✅ 加载TFLite神经网络模型（纯float32格式）
- ✅ 将FEN格式棋局转换为模型输入
- ✅ 评估棋盘位置（返回-1到1之间的分数）
- ✅ 完整的走法生成器（所有国际象棋规则）
- ✅ Alpha-Beta搜索算法（1层深度）
- ✅ 串口命令接口（eval、bestmove、help）
- ✅ ESP-NN加速优化

### 待改进功能

- ⏳ 模型评估准确度提升（30% → 目标80%+）
- ⏳ 模型大小优化（639KB → 目标<500KB）
- ⏳ 搜索深度优化（1层 → 目标3-4层）

## 模型信息

- **模型大小**: 639KB (纯float32)
- **输入**: 8x8x12 棋盘张量
- **输出**: 位置评估值 (-1到1)
- **推理时间**: ~334ms (ESP32-P4 @ 400MHz)
- **参数量**: 158,753
- **Flash占用**: 998KB / 1MB (99%)

## 测试

### 串口命令测试

程序启动后会显示命令提示符，可以输入以下命令测试：

```bash
# 测试help命令
help

# 测试eval命令（起始位置）
eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

# 测试eval命令（意大利开局）
eval r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3

# 测试bestmove命令
bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### Python脚本测试

```bash
# 测试ESP32串口通信
python test_chess_ai.py

# 测试看门狗功能
python test_watchdog.py

# 测试走法生成器
python test_movegen_simple.py
```

### 图形界面测试

```bash
# 启动图形界面
python chess_gui.py
```

## 性能优化建议

1. **模型优化**
   - 使用int8量化减少模型大小（需验证TFLite Micro支持）
   - 剪枝不重要的权重
   - 减少CNN层数或通道数

2. **搜索优化**
   - 增加搜索深度（1层 → 3-4层）
   - 实现移动排序（优先评估好的走法）
   - 添加迭代加深搜索

3. **硬件优化**
   - 启用ESP-NN加速（已启用）
   - 使用PSRAM存储更大的模型
   - 优化TensorFlow Lite Micro配置

## 故障排查

### 编译错误

```bash
# 清理构建缓存
idf.py fullclean
idf.py reconfigure
```

### 内存不足

修改 `chess_ai.c` 中的 `kTensorArenaSize`：

```c
constexpr int kTensorArenaSize = 300 * 1024;  // 增加到300KB
```

### 模型加载失败

检查 `chess_model.h` 文件是否正确生成，确保模型数据完整。

## 参考资料

- [ESP32-P4 技术参考手册](https://www.espressif.com/sites/default/files/documentation/esp32-p4_technical_reference_manual_cn.pdf)
- [TensorFlow Lite for Microcontrollers](https://www.tensorflow.org/lite/microcontrollers)
- [ESP-IDF 编程指南](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32p4/)