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

# 测试bestmove命令
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
cmd = f"bestmove {fen}\n"

print(f"发送: {cmd.strip()}")
# 每个字符延迟15ms，更慢的发送速度
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.015)

print("等待计算完成（约7秒）...")
time.sleep(8)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

ser.close()
print("\n测试完成")