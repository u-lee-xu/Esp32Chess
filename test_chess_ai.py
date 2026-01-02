import serial
import time

# 配置串口
ser = serial.Serial('COM19', 115200, timeout=2)
time.sleep(1)  # 等待串口就绪

# 测试函数
def send_command(cmd):
    print(f"\n>>> 发送命令: {cmd}")
    # 添加字符间延迟，避免字符丢失
    for char in cmd + '\n':
        ser.write(char.encode())
        time.sleep(0.005)  # 5ms延迟
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"<<< 响应:\n{response}")
    return response

# 清空缓冲区
ser.read_all()

# 测试1：显示帮助信息
print("\n" + "="*50)
print("测试1: 显示帮助信息")
print("="*50)
send_command("help")
time.sleep(1)

# 测试2：评估起始位置
print("\n" + "="*50)
print("测试2: 评估起始位置")
print("="*50)
fen_start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
send_command(f"eval {fen_start}")
time.sleep(1)

# 测试3：评估意大利开局
print("\n" + "="*50)
print("测试3: 评估意大利开局")
print("="*50)
fen_italian = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
send_command(f"eval {fen_italian}")
time.sleep(1)

# 测试4：评估西西里防御
print("\n" + "="*50)
print("测试4: 评估西西里防御")
print("="*50)
fen_sicilian = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
send_command(f"eval {fen_sicilian}")
time.sleep(1)

# 测试5：评估中局位置
print("\n" + "="*50)
print("测试5: 评估中局位置")
print("="*50)
fen_midgame = "r4rk1/pp2ppbp/2p3p1/8/2BP2n1/2N1P3/PP3PPP/R3KB1R w KQ - 0 12"
send_command(f"eval {fen_midgame}")
time.sleep(1)

# 测试6：评估残局位置
print("\n" + "="*50)
print("测试6: 评估残局位置")
print("="*50)
fen_endgame = "8/8/8/8/8/4P3/3PK3/8 w - - 0 1"
send_command(f"eval {fen_endgame}")
time.sleep(1)

print("\n" + "="*50)
print("测试完成!")
print("="*50)

# 关闭串口
ser.close()