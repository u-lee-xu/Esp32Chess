# -*- coding: utf-8 -*-
"""测试Stockfish是否正常工作"""
import subprocess
import time

print("Testing Stockfish...")

# Stockfish路径
stockfish_path = r"C:\Users\Mia\Documents\esp32chess\stockfish\stockfish\stockfish-windows-x86-64-avx2.exe"

try:
    # 启动Stockfish
    proc = subprocess.Popen(
        [stockfish_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    print("Stockfish started")

    # 发送UCI命令
    proc.stdin.write("uci\n")
    proc.stdin.flush()

    # 读取响应
    print("Reading UCI response...")
    for i in range(10):
        line = proc.stdout.readline()
        if line:
            print(f"Line {i}: {line.strip()}")
            if "uciok" in line:
                break
        time.sleep(0.1)

    # 测试评估
    print("\nTesting position evaluation...")
    proc.stdin.write("position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\n")
    proc.stdin.flush()

    proc.stdin.write("go depth 10\n")
    proc.stdin.flush()

    print("Reading evaluation...")
    for i in range(50):
        line = proc.stdout.readline()
        if line:
            print(f"Line {i}: {line.strip()}")
            if "bestmove" in line:
                break
        time.sleep(0.1)

    # 关闭
    proc.stdin.write("quit\n")
    proc.stdin.flush()
    proc.terminate()

    print("\n[OK] Stockfish test completed successfully")

except Exception as e:
    print(f"[ERROR] Stockfish test failed: {e}")