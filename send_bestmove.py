import serial
import time

ser = serial.Serial('COM19', 115200, timeout=1)
time.sleep(2)  # Wait for ESP32 to start

cmd = 'bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\r\n'
for c in cmd:
    ser.write(c.encode())
    time.sleep(0.01)  # 10ms delay between characters
print('Command sent')

start = time.time()
while time.time() - start < 30:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        print(data.decode('utf-8', errors='ignore'), end='')
    time.sleep(0.1)

ser.close()