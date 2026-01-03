#!/usr/bin/env python3
"""
ESP32国际象棋AI - 简单使用示例
展示如何：
1. 输入棋盘状态（FEN格式）
2. 获取AI评估
3. 获取最佳走法
"""

import serial
import time

# 配置
PORT = 'COM19'
BAUD = 115200

def connect_esp32():
    """连接ESP32"""
    ser = serial.Serial(PORT, BAUD, timeout=30)
    time.sleep(2)
    ser.read_all()  # 清空缓冲区
    print(f"✓ 已连接到 {PORT}")
    return ser

def send_cmd(ser, cmd):
    """发送命令（带延迟避免字符丢失）"""
    for char in cmd:
        ser.write(char.encode())
        time.sleep(0.01)
    ser.write(b'\n')
    time.sleep(0.1)

def read_resp(ser, wait=1):
    """读取响应"""
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

# ========================================
# 示例：与AI下棋
# ========================================

print("ESP32国际象棋AI - 简单示例")
print("=" * 50)

# 1. 连接ESP32
ser = connect_esp32()

# 2. 定义棋盘状态（起始位置）
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
print(f"\n当前棋盘: {fen}")

# 3. 评估当前局面
print("\n--- 评估局面 ---")
send_cmd(ser, f"eval {fen}")
response = read_resp(ser, wait=1)
print(response)

# 4. 获取最佳走法
print("\n--- 计算最佳走法 ---")
print("(需要5-10秒...)")
send_cmd(ser, f"bestmove {fen}")
response = read_resp(ser, wait=15)
print(response)

# 5. 假设AI建议走e2e4，更新棋盘
print("\n--- 模拟对局 ---")
print("AI建议: e2e4")
print("我们接受这个走法...")

# 更新后的棋盘（e2e4走法后）
fen_after = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
print(f"\n新棋盘: {fen_after}")

# 6. 评估新局面
print("\n--- 评估新局面 ---")
send_cmd(ser, f"eval {fen_after}")
response = read_resp(ser, wait=1)
print(response)

# 7. 获取黑方的最佳走法
print("\n--- 计算黑方最佳走法 ---")
print("(需要5-10秒...)")
send_cmd(ser, f"bestmove {fen_after}")
response = read_resp(ser, wait=15)
print(response)

ser.close()
print("\n✓ 完成")

# ========================================
# FEN格式说明
# ========================================
"""
FEN (Forsyth-Edwards Notation) 格式：
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

字段说明：
1. 棋盘布局（8行，用/分隔）
   - 大写字母：白方棋子（P=兵, N=马, B=象, R=车, Q=后, K=王）
   - 小写字母：黑方棋子
   - 数字：连续空格数

2. 轮到谁走（w=白方, b=黑方）

3. 王车易位权限（KQkq）
   - K: 白方王翼易位
   - Q: 白方后翼易位
   - k: 黑方王翼易位
   - q: 黑方后翼易位

4. 过路兵目标格（-表示无）

5. 半回合计数

6. 回合数
"""

# ========================================
# 如何集成到实际下棋程序
# ========================================
"""
# 伪代码示例

def play_chess():
    # 初始化
    board = start_position()
    esp32 = connect_esp32()

    while not game_over:
        # 轮到白方（玩家）
        if is_white_turn:
            move = get_player_move()
            board = make_move(board, move)

        # 轮到黑方（AI）
        else:
            # 1. 获取当前FEN
            fen = board_to_fen(board)

            # 2. 发送给ESP32
            send_cmd(esp32, f"bestmove {fen}")

            # 3. 等待AI响应
            response = read_resp(esp32, wait=15)

            # 4. 解析最佳走法
            best_move = parse_best_move(response)  # 例如: "e2e4"

            # 5. 执行走法
            board = make_move(board, best_move)

        # 切换回合
        switch_turn()

    esp32.close()
"""