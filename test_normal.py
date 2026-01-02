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

# 测试1: 模拟人类输入速度发送help命令
print("测试1: 模拟人类输入速度发送help命令")
cmd = "help\n"
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.01)  # 每个字符之间10ms延迟
time.sleep(1)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

if "ESP32-P4 Chess AI Commands" in response:
    print("[OK] help命令被正确识别")
else:
    print("[WARNING] help命令可能未被正确识别")

print("\n" + "="*50 + "\n")

# 测试2: 发送eval命令（使用较慢速度）
print("测试2: 发送eval命令（起始位置）")
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
cmd = f'eval {fen}\n'
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.005)  # FEN字符串每个字符之间5ms延迟
time.sleep(2)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

if "Evaluation:" in response:
    print("[OK] eval命令被正确识别")
else:
    print("[WARNING] eval命令可能未被正确识别")

ser.close()
print("\n测试完成")