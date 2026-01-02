import serial
import time

# 配置串口
ser = serial.Serial('COM19', 115200, timeout=1)
ser.reset_input_buffer()

print("Reading from COM19 (ESP32-P4)...")
print("Press Ctrl+C to stop\n")

try:
    for _ in range(50):  # 读取50次
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').rstrip()
            if line:
                print(line)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

ser.close()
print("\nDone.")