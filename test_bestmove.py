import serial
import time

# 配置串口
ser = serial.Serial('COM19', 115200, timeout=10)

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

# 测试bestmove命令
print("测试bestmove命令（起始位置）")
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
cmd = f'bestmove {fen}\n'
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.005)
time.sleep(3)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

if "bestmove" in response.lower() or "move" in response.lower():
    print("[OK] bestmove命令被识别")
else:
    print("[WARNING] bestmove命令可能未正常工作")

ser.close()
print("\n测试完成")