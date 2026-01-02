import serial
import time

# 配置串口
ser = serial.Serial('COM19', 115200, timeout=5)

# 清空缓冲区
time.sleep(1)
ser.read_all()

# 发送help命令
print("发送: help")
ser.write(b'help\n')
time.sleep(1)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

# 发送eval命令（起始位置）
print("发送: eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
ser.write(b'eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\n')
time.sleep(3)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

ser.close()
print("测试完成")