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

# 发送help命令
print("发送: help")
ser.write(b'help\n')
time.sleep(1)
response = ser.read_all().decode('utf-8', errors='ignore')
print(f"响应:\n{response}\n")

# 检查是否有看门狗警告
if 'task_wdt' in response:
    print("[WARNING] 仍有看门狗警告")
else:
    print("[OK] 没有看门狗警告")

# 等待一段时间，看是否有新的看门狗警告
print("\n等待10秒，检查是否有新的看门狗警告...")
time.sleep(10)
response = ser.read_all().decode('utf-8', errors='ignore')
if 'task_wdt' in response:
    print("[WARNING] 检测到看门狗警告")
    print(f"警告内容:\n{response}")
else:
    print("[OK] 没有新的看门狗警告")

ser.close()
print("\n测试完成")