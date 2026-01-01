# ESP32-P4 Chess AI

基于TensorFlow Lite Micro的国际象棋位置评估AI，部署到ESP32-P4芯片。

## 硬件要求

- ESP32-P4开发板
- USB数据线

## 软件要求

- ESP-IDF v5.3或更高版本
- Python 3.8+
- CMake 3.16+

## 编译步骤

### 1. 安装ESP-IDF

```bash
# 克隆ESP-IDF仓库
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
git checkout v5.3
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
idf.py -p /dev/ttyUSB0 flash
idf.py -p /dev/ttyUSB0 monitor
```

## 功能说明

### 当前实现

- ✅ 加载TFLite神经网络模型
- ✅ 将FEN格式棋局转换为模型输入
- ✅ 评估棋盘位置（返回-1到1之间的分数）
- ✅ 基础测试用例

### 待实现功能

- ⏳ 完整的走法生成器
- ⏳ 走法合法性验证
- ⏳ Alpha-Beta搜索算法
- ⏳ 串口命令接口
- ⏳ Web界面（可选）

## 模型信息

- **模型大小**: 170KB (量化后)
- **输入**: 8x8x12 棋盘张量
- **输出**: 位置评估值 (-1到1)
- **推理时间**: ~10-20ms (ESP32-P4 @ 400MHz)

## 测试

程序启动后会自动测试两个棋局位置：

1. 起始位置: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
2. 中局位置: `r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3`

## 性能优化建议

1. 使用PSRAM存储更大的模型
2. 启用NEON指令集加速
3. 优化TensorFlow Lite Micro配置
4. 使用多核并行处理

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