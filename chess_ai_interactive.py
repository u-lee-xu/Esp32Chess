#!/usr/bin/env python3
"""
ESP32国际象棋AI交互式调试脚本
功能：
1. 连接ESP32串口
2. 发送FEN格式的棋盘状态
3. 获取AI评估和最佳走法
4. 显示棋盘和走法
"""

import serial
import time
import sys

# 串口配置
SERIAL_PORT = 'COM19'
BAUD_RATE = 115200
TIMEOUT = 30  # bestmove可能需要5-10秒

class ChessAI:
    def __init__(self, port=SERIAL_PORT, baudrate=BAUD_RATE):
        """初始化串口连接"""
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connect()

    def connect(self):
        """连接ESP32"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=TIMEOUT)
            print(f"✓ 已连接到 {self.port}")
            print(f"✓ 波特率: {self.baudrate}")
            print()

            # 清空缓冲区
            time.sleep(2)
            self.ser.read_all()

            # 读取启动日志
            print("等待ESP32启动...")
            time.sleep(1)
            response = self.ser.read_all().decode('utf-8', errors='ignore')
            if 'ESP-NN' in response:
                print("✓ ESP-NN硬件加速已启用")
            print()

        except Exception as e:
            print(f"✗ 连接失败: {e}")
            sys.exit(1)

    def send_command(self, cmd):
        """发送命令到ESP32"""
        # 添加字符间延迟，避免字符丢失
        cmd_bytes = cmd.encode()
        for char in cmd_bytes:
            self.ser.write(bytes([char]))
            time.sleep(0.01)  # 10ms延迟

        # 发送换行
        self.ser.write(b'\n')
        time.sleep(0.1)

    def read_response(self, wait_time=1):
        """读取ESP32响应"""
        time.sleep(wait_time)
        response = self.ser.read_all().decode('utf-8', errors='ignore')
        return response

    def evaluate_position(self, fen):
        """评估棋盘位置"""
        print(f"评估位置: {fen[:50]}...")
        self.send_command(f"eval {fen}")
        response = self.read_response(wait_time=1)
        return response

    def get_best_move(self, fen):
        """获取最佳走法"""
        print(f"计算最佳走法: {fen[:50]}...")
        print("(这可能需要5-10秒，请耐心等待...)")
        self.send_command(f"bestmove {fen}")
        response = self.read_response(wait_time=15)  # 等待15秒
        return response

    def show_help(self):
        """显示帮助信息"""
        self.send_command("help")
        response = self.read_response(wait_time=1)
        print(response)

    def print_board(self, fen):
        """打印棋盘（简化版）"""
        board_part = fen.split()[0]
        rows = board_part.split('/')
        print("\n棋盘状态:")
        print("  a b c d e f g h")
        for i, row in enumerate(rows, start=8):
            print(f"{i} ", end="")
            for piece in row:
                if piece.isdigit():
                    print("  " * int(piece), end="")
                else:
                    print(piece + " ", end="")
            print()

    def close(self):
        """关闭连接"""
        if self.ser:
            self.ser.close()
            print("\n连接已关闭")

def main():
    """主函数"""
    print("=" * 60)
    print("      ESP32国际象棋AI - 交互式调试工具")
    print("=" * 60)
    print()

    # 连接ESP32
    ai = ChessAI()

    # 显示帮助
    print("可用命令:")
    ai.show_help()
    print()

    # 示例1：评估起始位置
    print("=" * 60)
    print("示例1: 评估起始位置")
    print("=" * 60)
    start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    ai.print_board(start_fen)
    response = ai.evaluate_position(start_fen)
    print(response)
    print()

    # 示例2：获取最佳走法
    print("=" * 60)
    print("示例2: 获取最佳走法")
    print("=" * 60)
    response = ai.get_best_move(start_fen)
    print(response)
    print()

    # 示例3：评估意大利开局
    print("=" * 60)
    print("示例3: 评估意大利开局")
    print("=" * 60)
    italian_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    ai.print_board(italian_fen)
    response = ai.evaluate_position(italian_fen)
    print(response)
    print()

    # 交互式模式
    print("=" * 60)
    print("交互式模式")
    print("=" * 60)
    print("输入FEN字符串或命令（输入'quit'退出）:")
    print()

    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("退出...")
                break

            elif user_input.lower() == 'help':
                ai.show_help()

            elif user_input.lower().startswith('eval '):
                fen = user_input[5:]
                ai.print_board(fen)
                response = ai.evaluate_position(fen)
                print(response)

            elif user_input.lower().startswith('bestmove '):
                fen = user_input[10:]
                ai.print_board(fen)
                response = ai.get_best_move(fen)
                print(response)

            else:
                print("未知命令。使用 'help' 查看帮助。")

        except KeyboardInterrupt:
            print("\n退出...")
            break
        except Exception as e:
            print(f"错误: {e}")

    ai.close()

if __name__ == "__main__":
    main()