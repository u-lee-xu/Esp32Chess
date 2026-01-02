# ESP32-P4 Chess AI - 项目文件索引

## 项目概述

本项目是一个基于TensorFlow Lite Micro的国际象棋AI，部署到ESP32-P4芯片上，包含神经网络模型、走法生成器和串口命令界面。

---

## ⚠️ 重要提示（请AI助手仔细阅读）

**每次开始工作前，请务必先阅读本文档的"文件保留与更新策略"章节！**

本文件包含了项目所有文件的详细分类和用途说明，以及：
- 哪些文件需要保留到Git
- 哪些文件是编译生成的（可以删除）
- 哪些文件是外部依赖（不建议提交）
- 文件的更新频率和备份策略

这样可以避免误删除重要文件，或提交不应该提交的文件到Git仓库。

**关键章节参考**：
- "文件保留与更新策略" - 了解文件分类和管理
- "文件重要性分级" - 了解哪些是核心文件
- "维护建议" - 了解如何维护项目

---

## 目录结构

```
esp32chess/
├── 项目根目录
│   ├── 文档文件 (*.md)
│   ├── Python脚本 (*.py)
│   ├── 数据文件 (*.json, *.pgn)
│   ├── 模型文件 (models/)
│   ├── ESP32项目 (esp32_chess_ai/)
│   ├── ESP-IDF源码 (esp-idf-v5.5.2/)
│   ├── Stockfish引擎 (stockfish/)
│   └── 开发板文档 (WT9932P4-TINY_*.pdf)
```

---

## 1. 项目根目录文件

### 1.1 文档文件 (*.md)

#### PROJECT_LOG.md
- **大小**: 64,715 字节
- **最后更新**: 2026-01-01
- **用途**: 完整的项目开发日志
- **内容**:
  - 数据准备阶段（PGN下载、解析）
  - 模型训练阶段（网络架构、训练参数）
  - 模型测试阶段（测试结果、问题分析）
  - 改进方案阶段（Stockfish评估生成）
  - ESP32部署阶段（编译、烧录、测试）
  - 问题记录和解决方案
  - 技术要点总结
- **重要性**: ⭐⭐⭐⭐⭐ (项目完整历史记录)

#### README_CURRENT_STATUS.md
- **大小**: 3,615 字节
- **最后更新**: 2026-01-01
- **用途**: 当前项目状态摘要
- **内容**:
  - 项目概述和完成度
  - 已完成功能列表
  - 可用命令说明
  - 硬件信息
  - 编译和烧录步骤
  - 重要注意事项（串口时序、Flash空间）
  - 未实现功能
  - 性能指标
  - 常见问题
- **重要性**: ⭐⭐⭐⭐ (快速了解项目状态)

#### STOCKFISH_SETUP.md
- **大小**: 3,594 字节
- **最后更新**: 2025-12-31
- **用途**: Stockfish引擎安装和使用指南
- **内容**:
  - Stockfish介绍
  - 下载和安装步骤
  - 配置说明
  - 评估生成流程
  - 数据转换方法
- **重要性**: ⭐⭐⭐ (模型改进阶段使用)

#### FILE_INDEX.md (本文件)
- **大小**: 待定
- **最后更新**: 2026-01-02
- **用途**: 项目文件索引和用途说明
- **内容**: 所有项目文件的详细说明
- **重要性**: ⭐⭐⭐⭐⭐ (项目导航和维护)

### 1.2 Python脚本 (*.py)

#### parse_pgn.py
- **用途**: 解析PGN文件，提取对局数据
- **输入**: PGN文件
- **输出**: chess_training_data.json
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐⭐ (数据准备阶段)

#### train_model.py
- **用途**: 训练神经网络模型
- **输入**: chess_training_data.json
- **输出**: chess_ai_model.keras, chess_ai_model.tflite
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐⭐⭐ (模型训练)

#### test_model.py
- **用途**: 测试模型评估准确度
- **输入**: 无（内置测试用例）
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐ (模型验证)

#### analyze_data.py
- **用途**: 分析训练数据质量
- **输入**: chess_training_data.json
- **输出**: 数据统计报告
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐ (数据分析)

#### generate_evaluations.py
- **用途**: 使用Stockfish生成评估值
- **输入**: PGN文件
- **输出**: chess_training_data_with_eval.json
- **状态**: ✅ 已完成（未运行）
- **重要性**: ⭐⭐⭐⭐ (模型改进)

#### movegen.py
- **用途**: Python走法生成器（用于测试）
- **输入**: FEN字符串
- **输出**: 合法走法列表
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐⭐ (走法生成器验证)

#### test_chess_ai.py
- **用途**: 测试ESP32串口通信和命令
- **输入**: 无（内置测试用例）
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐⭐ (ESP32测试)

#### test_normal.py
- **用途**: 正常速度串口测试
- **输入**: 无
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐ (串口测试)

#### test_slow.py
- **用途**: 慢速串口测试（字符间延迟）
- **输入**: 无
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐ (串口测试)

#### test_watchdog.py
- **用途**: 测试看门狗功能
- **输入**: 无
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐ (系统稳定性测试)

#### test_stockfish.py
- **用途**: 测试Stockfish引擎
- **输入**: 无
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐ (Stockfish验证)

#### test_movegen_simple.py
- **用途**: 走法生成器简化测试
- **输入**: 无（内置测试用例）
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐⭐⭐ (走法生成器测试)

#### check_bin.py
- **用途**: 检查二进制文件
- **输入**: 二进制文件路径
- **输出**: 文件信息
- **状态**: ✅ 已完成
- **重要性**: ⭐ (调试工具)

#### check_data.py
- **用途**: 检查数据文件
- **输入**: 数据文件路径
- **输出**: 数据统计
- **状态**: ✅ 已完成
- **重要性**: ⭐ (调试工具)

#### check_header.py
- **用途**: 检查C头文件
- **输入**: 头文件路径
- **输出**: 头文件信息
- **状态**: ✅ 已完成
- **重要性**: ⭐ (调试工具)

#### quick_test.py
- **用途**: 快速测试脚本
- **输入**: 无
- **输出**: 测试结果
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐ (快速验证)

#### read_serial.py
- **用途**: 读取串口数据
- **输入**: 串口配置
- **输出**: 串口数据
- **状态**: ✅ 已完成
- **重要性**: ⭐⭐ (调试工具)

### 1.3 数据文件

#### chess_training_data.json
- **大小**: 278,797,719 字节 (约278MB)
- **用途**: 训练数据（无评估值）
- **样本数**: 20,002个
- **来源**: 500局PGN对局
- **状态**: ✅ 已生成
- **重要性**: ⭐⭐⭐⭐ (旧版训练数据)

#### chess_training_data_with_eval.json
- **大小**: 待定
- **用途**: 训练数据（带Stockfish评估值）
- **样本数**: 待定
- **来源**: Stockfish评估生成
- **状态**: ⏳ 待生成
- **重要性**: ⭐⭐⭐⭐⭐ (新版训练数据)

#### lichess_tournament_2025.12.31_C5W0R90y_hourly-ultrabullet.pgn
- **大小**: 约5MB
- **用途**: PGN对局数据源
- **对局数**: 500局
- **时控**: 15+0
- **状态**: ✅ 已下载
- **重要性**: ⭐⭐⭐⭐ (原始数据)

### 1.4 模型文件 (models/)

#### chess_ai_model.keras
- **大小**: 1.89 MB
- **格式**: Keras SavedModel
- **用途**: PC端训练和推理
- **状态**: ✅ 已生成
- **重要性**: ⭐⭐⭐⭐⭐ (主模型)

#### chess_ai_model.tflite
- **大小**: 639 KB
- **格式**: TFLite FlatBuffer (纯float32)
- **用途**: ESP32部署
- **状态**: ✅ 已生成
- **重要性**: ⭐⭐⭐⭐⭐ (ESP32模型)

#### chess_model.h
- **大小**: 约600KB
- **格式**: C头文件
- **用途**: 嵌入ESP32固件
- **状态**: ✅ 已生成
- **重要性**: ⭐⭐⭐⭐⭐ (固件集成)

#### best_model.keras
- **大小**: 1.89 MB
- **格式**: Keras SavedModel
- **用途**: 验证集上表现最佳的模型
- **状态**: ✅ 已生成
- **重要性**: ⭐⭐⭐ (模型备份)

---

## 2. ESP32项目文件 (esp32_chess_ai/)

### 2.1 文档文件 (*.md)

#### README.md
- **大小**: 2,335 字节
- **用途**: ESP32项目说明
- **内容**:
  - 硬件和软件要求
  - 编译步骤
  - 功能说明
  - 模型信息
  - 测试方法
  - 性能优化建议
  - 故障排查
- **重要性**: ⭐⭐⭐⭐ (ESP32项目文档)

#### QUICKSTART.md
- **大小**: 3,651 字节
- **用途**: 快速开始指南
- **内容**:
  - 环境准备
  - 快速编译和烧录
  - 基本测试
- **重要性**: ⭐⭐⭐⭐ (新手指南)

#### COMMANDS.md
- **大小**: 3,368 字节
- **用途**: 命令使用说明
- **内容**:
  - eval命令
  - bestmove命令
  - help命令
  - 命令格式和示例
- **重要性**: ⭐⭐⭐ (用户手册)

#### PYTHON_DEPENDENCIES.md
- **大小**: 8,303 字节
- **用途**: Python依赖管理文档
- **内容**:
  - ESP-IDF核心依赖列表
  - 版本冲突解决方案
  - 安装命令
  - 验证方法
  - 常见问题
- **重要性**: ⭐⭐⭐⭐⭐ (依赖管理)

### 2.2 编译脚本 (*.bat)

#### build.bat
- **大小**: 1,413 字节
- **用途**: 标准编译脚本
- **功能**:
  - 设置ESP-IDF环境
  - 设置目标芯片为ESP32-P4
  - 编译项目
- **状态**: ✅ 可用
- **重要性**: ⭐⭐⭐⭐⭐ (主要编译脚本)
- **使用**: `build.bat`

#### build_skip_check.bat
- **大小**: 515 字节
- **用途**: 跳过Python依赖检查的编译脚本
- **功能**:
  - 设置ESP-IDF环境
  - 跳过依赖检查
  - 编译项目
- **状态**: ✅ 可用
- **重要性**: ⭐⭐⭐ (调试用)
- **使用**: `build_skip_check.bat`

#### build_temp.bat
- **大小**: 794 字节
- **用途**: 临时编译脚本
- **功能**: 临时编译配置
- **状态**: ⏳ 待定
- **重要性**: ⭐ (临时工具)

#### config_build.bat
- **大小**: 893 字节
- **用途**: 配置并编译
- **功能**:
  - 配置项目
  - 编译项目
- **状态**: ✅ 可用
- **重要性**: ⭐⭐ (配置工具)

#### flash.bat
- **大小**: 1,324 字节
- **用途**: 烧录固件到ESP32
- **功能**:
  - 设置ESP-IDF环境
  - 获取COM端口
  - 烧录固件
  - 启动监视器
- **状态**: ✅ 可用
- **重要性**: ⭐⭐⭐⭐⭐ (烧录脚本)
- **使用**: `flash.bat`

#### quick_compile.bat
- **大小**: 451 字节
- **用途**: 快速编译脚本
- **功能**: 直接运行idf.py build
- **状态**: ✅ 可用
- **重要性**: ⭐⭐ (快速编译)

#### rebuild.bat
- **大小**: 1,015 字节
- **用途**: 重新编译脚本
- **功能**:
  - 清理构建缓存
  - 重新配置
  - 重新编译
- **状态**: ✅ 可用
- **重要性**: ⭐⭐⭐ (重新编译)

#### rebuild_movegen.bat
- **大小**: 1,139 字节
- **用途**: 重新编译走法生成器版本
- **功能**:
  - 设置环境变量
  - 清理构建缓存
  - 重新编译
- **状态**: ✅ 可用
- **重要性**: ⭐⭐⭐⭐ (走法生成器编译)

### 2.3 配置文件

#### CMakeLists.txt
- **大小**: 110 字节
- **用途**: 项目级CMake配置
- **内容**: 包含main组件
- **重要性**: ⭐⭐⭐⭐⭐ (构建系统)

#### sdkconfig
- **大小**: 76,097 字节
- **用途**: ESP-IDF配置文件（当前）
- **内容**: 所有ESP-IDF配置选项
- **重要性**: ⭐⭐⭐⭐⭐ (系统配置)

#### sdkconfig.defaults
- **大小**: 400 字节
- **用途**: ESP-IDF默认配置
- **内容**: 项目特定的默认配置
- **重要性**: ⭐⭐⭐⭐ (项目配置)

#### sdkconfig.old
- **大小**: 78,806 字节
- **用途**: ESP-IDF配置文件（旧版本）
- **内容**: 之前的配置备份
- **重要性**: ⭐⭐ (配置备份)

#### dependencies.lock
- **大小**: 982 字节
- **用途**: 组件依赖锁文件
- **内容**: 组件版本锁定
- **重要性**: ⭐⭐⭐ (依赖管理)

### 2.4 源代码 (main/)

#### chess_ai.cpp
- **大小**: 约1,000行
- **用途**: 主程序文件
- **内容**:
  - TensorFlow Lite Micro集成
  - 走法生成器
  - 串口命令处理
  - FEN解析
  - 棋盘管理
- **状态**: ✅ 已完成（包含走法生成器）
- **重要性**: ⭐⭐⭐⭐⭐ (核心代码)

#### chess_model.h
- **大小**: 约600KB
- **用途**: TFLite模型头文件
- **内容**: 模型字节数组
- **重要性**: ⭐⭐⭐⭐⭐ (模型数据)

#### CMakeLists.txt
- **用途**: 组件级CMake配置
- **内容**: 源文件列表、依赖库
- **重要性**: ⭐⭐⭐⭐⭐ (构建系统)

---

## 3. ESP-IDF源码 (esp-idf-v5.5.2/)

### 3.1 Requirements文件 (tools/requirements/)

#### requirements.core.txt
- **大小**: 839 字节
- **用途**: ESP-IDF核心Python依赖
- **内容**: 30+个必需包（无版本约束）
- **重要性**: ⭐⭐⭐⭐⭐ (核心依赖)
- **使用**: `pip install -r requirements.core.txt`

#### requirements.ci.txt
- **大小**: 484 字节
- **用途**: CI/CD系统依赖
- **内容**: 持续集成所需的包
- **重要性**: ⭐⭐ (CI/CD)

#### requirements.docs.txt
- **大小**: 417 字节
- **用途**: 文档生成依赖
- **内容**: 生成文档所需的包
- **重要性**: ⭐⭐ (文档生成)

#### requirements.gdbgui.txt
- **大小**: 773 字节
- **用途**: GDB GUI调试器依赖
- **内容**: 图形化GDB调试器所需的包
- **重要性**: ⭐⭐⭐ (调试)

#### requirements.ide.txt
- **大小**: 404 字节
- **用途**: IDE集成依赖
- **内容**: IDE集成所需的包
- **重要性**: ⭐⭐ (IDE支持)

#### requirements.pytest.txt
- **大小**: 583 字节
- **用途**: 单元测试依赖
- **内容**: pytest测试框架
- **重要性**: ⭐⭐⭐ (测试)

#### requirements.test-specific.txt
- **大小**: 436 字节
- **用途**: 特定测试依赖
- **内容**: 特定测试场景所需的包
- **重要性**: ⭐⭐ (测试)

---

## 4. Stockfish引擎 (stockfish/)

### 4.1 源码文件

#### stockfish-windows-x86-64-avx2.exe
- **大小**: 待定
- **用途**: Stockfish Windows可执行文件
- **架构**: x86-64 AVX2
- **状态**: ✅ 已安装
- **重要性**: ⭐⭐⭐⭐⭐ (评估生成)

#### src/
- **用途**: Stockfish源代码
- **内容**: C++源文件
- **重要性**: ⭐⭐ (源码参考)

---

## 5. 开发板文档

### 5.1 PDF文档

#### WT9932P4-TINY_使用指南_V1.1.pdf
- **用途**: 开发板使用指南
- **内容**:
  - 硬件介绍
  - 快速开始
  - 引脚定义
  - 示例代码
- **重要性**: ⭐⭐⭐⭐ (硬件参考)

#### WT9932P4-TINY_引脚定义_V1.1.pdf
- **用途**: 引脚定义文档
- **内容**:
  - 完整引脚图
  - 引脚功能说明
  - 电气特性
- **重要性**: ⭐⭐⭐⭐⭐ (硬件设计)

#### WT9932P4-TINY_SCH_V1.3.pdf
- **用途**: 原理图
- **内容**:
  - 电路原理图
  - 元件清单
  - PCB布局
- **重要性**: ⭐⭐⭐ (硬件调试)

#### WT9932P4-TINY_HDK_V1.1.zip
- **用途**: 硬件开发包
- **内容**:
  - 原理图源文件
  - PCB设计文件
  - 参考设计
- **重要性**: ⭐⭐ (硬件开发)

#### WT9932P4-TINY_Release_V1.0_20250807.zip
- **用途**: 发布版本
- **内容**:
  - 固件
  - 驱动
  - 工具
- **重要性**: ⭐⭐ (固件参考)

---

## 6. 其他文件

### 6.1 压缩包

#### stockfish-windows-x86-64-avx2.zip
- **大小**: 待定
- **用途**: Stockfish Windows版本压缩包
- **状态**: ✅ 已下载
- **重要性**: ⭐ (安装包备份)

#### stockfish.zip
- **大小**: 待定
- **用途**: Stockfish通用压缩包
- **状态**: ✅ 已下载
- **重要性**: ⭐ (安装包备份)

---

## 文件重要性分级

### ⭐⭐⭐⭐⭐ (核心文件，不可删除)
- PROJECT_LOG.md - 项目完整历史
- FILE_INDEX.md - 项目文件索引
- PYTHON_DEPENDENCIES.md - Python依赖管理
- chess_ai_model.keras - 主模型
- chess_ai_model.tflite - ESP32模型
- chess_model.h - 模型头文件
- chess_ai.cpp - 核心代码
- build.bat - 主要编译脚本
- flash.bat - 烧录脚本
- CMakeLists.txt (项目级) - 构建系统
- sdkconfig - 系统配置
- WT9932P4-TINY_引脚定义_V1.1.pdf - 硬件参考
- stockfish-windows-x86-64-avx2.exe - 评估引擎

### ⭐⭐⭐⭐ (重要文件)
- README_CURRENT_STATUS.md - 项目状态
- parse_pgn.py - 数据解析
- train_model.py - 模型训练
- generate_evaluations.py - 评估生成
- movegen.py - 走法生成器
- test_chess_ai.py - ESP32测试
- test_movegen_simple.py - 走法测试
- rebuild_movegen.bat - 走法编译
- README.md (ESP32) - 项目文档
- QUICKSTART.md - 快速开始
- requirements.core.txt - 核心依赖
- chess_training_data.json - 训练数据
- lichess_tournament_*.pgn - 原始数据

### ⭐⭐⭐ (辅助文件)
- STOCKFISH_SETUP.md - Stockfish指南
- test_model.py - 模型测试
- analyze_data.py - 数据分析
- test_normal.py - 串口测试
- test_slow.py - 串口测试
- test_watchdog.py - 看门狗测试
- COMMANDS.md - 命令说明
- build_skip_check.bat - 调试编译
- config_build.bat - 配置编译
- rebuild.bat - 重新编译
- requirements.gdbgui.txt - 调试依赖
- requirements.pytest.txt - 测试依赖
- best_model.keras - 模型备份
- WT9932P4-TINY_使用指南_V1.1.pdf - 使用指南

### ⭐⭐ (调试工具)
- check_bin.py - 二进制检查
- check_data.py - 数据检查
- check_header.py - 头文件检查
- quick_test.py - 快速测试
- read_serial.py - 串口读取
- build_temp.bat - 临时编译
- quick_compile.bat - 快速编译
- requirements.ci.txt - CI依赖
- requirements.docs.txt - 文档依赖
- requirements.ide.txt - IDE依赖
- requirements.test-specific.txt - 测试依赖
- chess_training_data_with_eval.json - 新版数据（待生成）
- sdkconfig.old - 配置备份
- dependencies.lock - 依赖锁定

### ⭐ (备份文件)
- stockfish-windows-x86-64-avx2.zip - 安装备份
- stockfish.zip - 安装备份
- WT9932P4-TINY_HDK_V1.1.zip - 开发包
- WT9932P4-TINY_Release_V1.0_20250807.zip - 发布包
- WT9932P4-TINY_SCH_V1.3.pdf - 原理图

---

## 文件生命周期

### 临时文件（可删除）
- build/ - 编译输出目录
- *.zip - 安装包（已安装后）
- sdkconfig.old - 旧配置备份

### 持久文件（需保留）
- 所有源代码文件
- 所有模型文件
- 所有文档文件
- 所有配置文件

### 待生成文件
- chess_training_data_with_eval.json - 新版训练数据
- build/esp32_chess_ai.bin - 新固件（编译中）
- build/esp32_chess_ai.elf - ELF文件（编译中）

---

## 维护建议

1. **定期清理**: 删除临时文件和旧的编译输出
2. **版本控制**: 将源代码和文档纳入Git管理
3. **备份模型**: 定期备份模型文件
4. **更新文档**: 每次修改后更新相关文档
5. **依赖管理**: 定期检查Python依赖版本

---

## 更新日志

- 2026-01-02: 创建FILE_INDEX.md，记录所有项目文件
- 2026-01-02: 创建PYTHON_DEPENDENCIES.md，记录Python依赖
- 2026-01-01: 更新chess_ai.cpp，添加走法生成器
- 2026-01-01: 更新PROJECT_LOG.md，记录ESP32部署过程
- 2025-12-31: 创建STOCKFISH_SETUP.md

---

## 文件保留与更新策略

### 需要保留到Git的文件（源代码和配置）

#### 根目录 - 源代码
- `parse_pgn.py` - PGN解析脚本
- `train_model.py` - 模型训练脚本
- `test_model.py` - 模型测试脚本
- `generate_evaluations.py` - 评估生成脚本
- `movegen.py` - 走法生成器（Python版）
- `test_chess_ai.py` - ESP32测试脚本
- `test_movegen_simple.py` - 走法生成器测试脚本
- `analyze_data.py` - 数据分析脚本
- `chess_training_data.json` - 训练数据（Git LFS）
- `chess_training_data_with_eval.json` - 训练数据（Git LFS）
- `lichess_tournament_*.pgn` - PGN对局数据（Git LFS）

#### 根目录 - 模型文件
- `models/chess_ai_model.keras` - Keras模型（Git LFS）
- `models/chess_ai_model.tflite` - TFLite模型（Git LFS）
- `models/best_model.keras` - 最佳模型（Git LFS）

#### 根目录 - 文档
- `PROJECT_LOG.md` - 项目日志
- `README_CURRENT_STATUS.md` - 项目状态
- `FILE_INDEX.md` - 文件索引（本文件）
- `STOCKFISH_SETUP.md` - Stockfish指南
- `requirements.txt` - Python依赖

#### ESP32项目 - 源代码
- `esp32_chess_ai/main/chess_ai.cpp` - 主程序
- `esp32_chess_ai/main/chess_model.h` - 模型头文件（Git LFS）
- `esp32_chess_ai/CMakeLists.txt` - 项目CMake配置
- `esp32_chess_ai/main/CMakeLists.txt` - 组件CMake配置
- `esp32_chess_ai/sdkconfig.defaults` - 默认配置
- `esp32_chess_ai/dependencies.lock` - 依赖锁定

#### ESP32项目 - 文档和脚本
- `esp32_chess_ai/README.md` - 项目说明
- `esp32_chess_ai/QUICKSTART.md` - 快速开始
- `esp32_chess_ai/COMMANDS.md` - 命令说明
- `esp32_chess_ai/PYTHON_DEPENDENCIES.md` - 依赖管理
- `esp32_chess_ai/*.bat` - 所有编译和烧录脚本

#### 开发板文档
- `WT9932P4-TINY_*.pdf` - 开发板文档（Git LFS）

---

### 编译生成的文件（可删除/更新）

#### ESP32编译输出
- `esp32_chess_ai/build/` - 整个编译输出目录
  - `build/esp32_chess_ai.bin` - 固件二进制
  - `build/esp32_chess_ai.elf` - ELF文件
  - `build/bootloader/` - bootloader
  - `build/partition_table/` - 分区表
  - `build/*.log` - 编译日志

#### Python缓存
- `__pycache__/` - Python字节码缓存
- `*.pyc` - Python字节码文件

#### 其他临时文件
- `sdkconfig` - 当前配置（可从sdkconfig.defaults重新生成）
- `build.log` - 编译日志

---

### 外部依赖（需保留但不建议提交到Git）

#### ESP-IDF源码
- `esp-idf-v5.5.2/` - ESP-IDF完整源码
  - **建议**: 使用Git子模块或单独管理
  - **原因**: 文件太大（数百MB）
  - **替代**: 使用官方ESP-IDF安装

#### Stockfish引擎
- `stockfish/` - Stockfish源码
- `stockfish-windows-x86-64-avx2.exe` - Stockfish可执行文件
- `stockfish.zip` - Stockfish压缩包
  - **建议**: 保留本地，不提交到Git
  - **原因**: 可从官网重新下载

#### 开发板资料
- `WT9932P4-TINY_HDK_V1.1.zip` - 硬件开发包
- `WT9932P4-TINY_Release_V1.0_20250807.zip` - 发布版本
  - **建议**: 保留本地，不提交到Git
  - **原因**: 厂商提供的资料

---

### Git配置建议

#### .gitignore应包含：
```
# 编译输出
esp32_chess_ai/build/
esp32_chess_ai/sdkconfig

# Python缓存
__pycache__/
*.pyc
*.pyo

# 临时文件
*.log
*.tmp

# 外部依赖
esp-idf-v5.5.2/
stockfish/
stockfish.zip
stockfish-windows-x86-64-avx2.zip

# 开发板资料
WT9932P4-TINY_HDK*.zip
WT9932P4-TINY_Release*.zip
```

#### Git LFS应管理：
- `chess_training_data.json`
- `chess_training_data_with_eval.json`
- `lichess_tournament_*.pgn`
- `models/*.keras`
- `models/*.tflite`
- `WT9932P4-TINY_*.pdf`
- `esp32_chess_ai/main/chess_model.h`

---

### 文件更新频率

#### 经常更新（每次修改）
- `chess_ai.cpp` - 核心代码
- `PROJECT_LOG.md` - 开发日志
- `FILE_INDEX.md` - 文件索引
- `sdkconfig` - 配置文件

#### 定期更新（功能变更时）
- `PYTHON_DEPENDENCIES.md` - 依赖管理
- `README_CURRENT_STATUS.md` - 项目状态
- `COMMANDS.md` - 命令说明
- `*.bat` - 编译脚本

#### 很少更新（版本发布时）
- `CMakeLists.txt` - 构建配置
- `sdkconfig.defaults` - 默认配置
- `README.md` - 项目文档
- `QUICKSTART.md` - 快速开始

#### 基本不更新（稳定后）
- `models/chess_ai_model.tflite` - TFLite模型
- `models/chess_model.h` - 模型头文件
- `WT9932P4-TINY_*.pdf` - 开发板文档

---

### 备份策略

#### 必须备份（不可恢复）
- `models/chess_ai_model.keras` - Keras模型源文件
- `chess_training_data.json` - 训练数据
- `PROJECT_LOG.md` - 完整开发历史

#### 建议备份（可重新生成）
- `chess_ai.cpp` - 可从Git恢复
- `*.py` 脚本 - 可从Git恢复
- `*.md` 文档 - 可从Git恢复

#### 无需备份（可重新编译）
- `build/` - 编译输出
- `esp32_chess_ai.bin` - 固件
- `*.log` - 日志文件

---

## 联系信息

- 项目仓库: https://github.com/u-lee-xu/Esp32Chess
- 最后更新: 2026年1月2日