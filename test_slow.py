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

# 慢速发送help命令，每个字符之间有延迟
cmd = "help\n"
print(f"发送命令（慢速）: {cmd.strip()}")
for char in cmd:
    ser.write(char.encode())
    time.sleep(0.05)  # 每个字符之间50ms延迟

time.sleep(1)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

# 检查命令是否被正确识别
if "ESP32-P4 Chess AI Commands" in response:
    print("[OK] help命令被正确识别")
else:
    print("[ERROR] help命令未被正确识别")

ser.close()
print("\n测试完成")