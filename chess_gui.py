#!/usr/bin/env python3
"""
ESP32国际象棋AI - 图形化对弈程序
功能：
- 图形化棋盘显示
- 鼠标点击走棋
- 连接ESP32获取AI走法
- 实时显示AI评估
"""

import tkinter as tk
from tkinter import messagebox
import serial
import time
import threading

# 配置
SERIAL_PORT = 'COM19'
BAUD_RATE = 115200
TIMEOUT = 30

# 棋子Unicode符号
PIECES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',  # 白方
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'   # 黑方
}

# 颜色
WHITE_SQUARE = '#F0D9B5'
BLACK_SQUARE = '#B58863'
SELECTED_COLOR = '#FFD700'
VALID_MOVE_COLOR = '#90EE90'
LAST_MOVE_COLOR = '#FFB6C1'

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32国际象棋AI")
        self.root.geometry("600x700")

        # 棋盘状态（8x8数组）
        self.board = self.create_initial_board()
        self.selected_square = None
        self.valid_moves = []
        self.last_move = None
        self.is_white_turn = True
        self.ai_thinking = False
        self.ai_mode = True  # AI模式：True=玩家vs AI, False=玩家vs 玩家

        # ESP32连接
        self.ser = None
        self.serial_lock = threading.Lock()  # 添加串口锁
        self.connect_esp32()

        # 创建UI
        self.create_widgets()

        # 不启动接收线程，采用简单模式：需要时才读取

    def create_initial_board(self):
        """创建初始棋盘"""
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

    def connect_esp32(self):
        """连接ESP32"""
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
            time.sleep(2)
            self.ser.read_all()
            
            # 测试连接：发送help命令
            print("[TEST] 测试ESP32连接...")
            cmd = "help\n"
            for char in cmd:
                self.ser.write(char.encode())
                time.sleep(0.02)
            time.sleep(0.5)
            
            # 读取响应
            response = self.ser.read_all().decode('utf-8', errors='ignore')
            if 'Commands' in response or '命令' in response:
                print("[OK] 已连接到ESP32（通信正常）")
            else:
                print("[WARNING] 已连接到ESP32，但通信可能有问题")
                print(f"[TEST] 响应: {response}")
                
        except Exception as e:
            print(f"[ERROR] 连接ESP32失败: {e}")
            messagebox.showerror("错误", f"无法连接ESP32: {e}")

    def create_widgets(self):
        """创建界面组件"""
        # 顶部信息栏
        self.info_frame = tk.Frame(self.root, height=50, bg='white')
        self.info_frame.pack(fill='x', padx=5, pady=5)

        self.turn_label = tk.Label(self.info_frame, text="轮到: 白方", font=('Arial', 14, 'bold'), bg='white')
        self.turn_label.pack(side='left', padx=10)

        self.eval_label = tk.Label(self.info_frame, text="评估: 0.00", font=('Arial', 12), bg='white')
        self.eval_label.pack(side='left', padx=10)

        self.status_label = tk.Label(self.info_frame, text="就绪", font=('Arial', 10), fg='green', bg='white')
        self.status_label.pack(side='right', padx=10)

        # 棋盘
        self.board_frame = tk.Frame(self.root, padx=10, pady=10)
        self.board_frame.pack()

        self.squares = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = WHITE_SQUARE if (row + col) % 2 == 0 else BLACK_SQUARE
                square = tk.Label(
                    self.board_frame,
                    text='',
                    font=('Arial', 32),
                    width=3,
                    height=2,
                    bg=color,
                    relief='ridge',
                    cursor='hand2'
                )
                square.grid(row=row, column=col)
                square.bind('<Button-1>', lambda e, r=row, c=col: self.on_square_click(r, c))
                self.squares[row][col] = square

        # 底部控制栏
        self.control_frame = tk.Frame(self.root, height=50, bg='white')
        self.control_frame.pack(fill='x', padx=5, pady=5)

        tk.Button(self.control_frame, text="新游戏", command=self.new_game, font=('Arial', 10)).pack(side='left', padx=5)
        tk.Button(self.control_frame, text="AI模式: 开", command=self.toggle_ai_mode, font=('Arial', 10)).pack(side='left', padx=5)
        tk.Button(self.control_frame, text="获取AI建议", command=self.get_ai_move, font=('Arial', 10)).pack(side='left', padx=5)
        tk.Button(self.control_frame, text="评估当前局面", command=self.evaluate_position, font=('Arial', 10)).pack(side='left', padx=5)

        self.update_board()

    def update_board(self):
        """更新棋盘显示"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                color = WHITE_SQUARE if (row + col) % 2 == 0 else BLACK_SQUARE

                # 高亮选中的格子
                if self.selected_square == (row, col):
                    color = SELECTED_COLOR
                # 高亮有效走法
                elif (row, col) in self.valid_moves:
                    color = VALID_MOVE_COLOR
                # 高亮上一步
                elif self.last_move and ((row, col) == self.last_move[0] or (row, col) == self.last_move[1]):
                    color = LAST_MOVE_COLOR

                # 显示棋子
                text = PIECES.get(piece, '') if piece else ''
                self.squares[row][col].config(text=text, bg=color)

        # 更新回合显示
        turn_text = "白方" if self.is_white_turn else "黑方"
        self.turn_label.config(text=f"轮到: {turn_text}")

    def on_square_click(self, row, col):
        """处理格子点击"""
        if self.ai_thinking:
            return

        piece = self.board[row][col]

        # 如果已经选中了棋子
        if self.selected_square:
            # 点击了有效走法格子
            if (row, col) in self.valid_moves:
                self.make_move(self.selected_square, (row, col))
                self.selected_square = None
                self.valid_moves = []
            # 点击了其他棋子
            elif piece and ((piece.isupper() and self.is_white_turn) or (piece.islower() and not self.is_white_turn)):
                self.selected_square = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
            # 取消选择
            else:
                self.selected_square = None
                self.valid_moves = []
        # 选择棋子
        elif piece and ((piece.isupper() and self.is_white_turn) or (piece.islower() and not self.is_white_turn)):
            self.selected_square = (row, col)
            self.valid_moves = self.get_valid_moves(row, col)

        self.update_board()

    def get_valid_moves(self, row, col):
        """获取有效走法（简化版）"""
        moves = []
        piece = self.board[row][col]
        if not piece:
            return moves

        # 简化的走法生成（只考虑基本移动）
        if piece.lower() == 'p':  # 兵
            direction = -1 if piece.isupper() else 1
            # 前进一格
            if 0 <= row + direction < 8 and not self.board[row + direction][col]:
                moves.append((row + direction, col))
                # 前进两格（起始位置）
                start_row = 6 if piece.isupper() else 1
                if row == start_row and not self.board[row + 2 * direction][col]:
                    moves.append((row + 2 * direction, col))
            # 吃子
            for dc in [-1, 1]:
                if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                    target = self.board[row + direction][col + dc]
                    if target and ((target.isupper() != piece.isupper()) if target else False):
                        moves.append((row + direction, col + dc))

        elif piece.lower() in ['r', 'q']:  # 车、后（直线）
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if not self.board[r][c]:
                        moves.append((r, c))
                    else:
                        if (self.board[r][c].isupper() != piece.isupper()) if self.board[r][c] else False:
                            moves.append((r, c))
                        break
                    r, c = r + dr, c + dc

        elif piece.lower() in ['b', 'q']:  # 象、后（斜线）
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if not self.board[r][c]:
                        moves.append((r, c))
                    else:
                        if (self.board[r][c].isupper() != piece.isupper()) if self.board[r][c] else False:
                            moves.append((r, c))
                        break
                    r, c = r + dr, c + dc

        elif piece.lower() == 'n':  # 马
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if not self.board[r][c] or (self.board[r][c].isupper() != piece.isupper()):
                        moves.append((r, c))

        elif piece.lower() == 'k':  # 王
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < 8 and 0 <= c < 8:
                        if not self.board[r][c] or (self.board[r][c].isupper() != piece.isupper()):
                            moves.append((r, c))

        return moves

    def make_move(self, from_sq, to_sq):
        """执行走法"""
        from_row, from_col = from_sq
        to_row, to_col = to_sq

        # 移动棋子
        piece = self.board[from_row][from_col]
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''

        # 兵升变（自动升变为后）
        if piece.lower() == 'p' and (to_row == 0 or to_row == 7):
            self.board[to_row][to_col] = 'Q' if piece.isupper() else 'q'

        self.last_move = (from_sq, to_sq)
        self.is_white_turn = not self.is_white_turn
        self.update_board()

        # 检查游戏结束
        self.check_game_over()

        # AI模式：轮到黑方时自动走棋
        if self.ai_mode and not self.is_white_turn and not self.ai_thinking:
            self.root.after(500, self.get_ai_move)  # 延迟500ms后自动走棋

    def make_ai_move(self, move_str, score):
        """执行AI返回的走法（格式: 'b8c6'）"""
        try:
            # 解析走法字符串（例如: "b8c6"）
            if len(move_str) != 4:
                raise ValueError(f"无效的走法格式: {move_str}")

            # 转换为坐标
            from_col = ord(move_str[0]) - ord('a')
            from_row = 8 - int(move_str[1])
            to_col = ord(move_str[2]) - ord('a')
            to_row = 8 - int(move_str[3])

            # 执行走法
            self.make_move((from_row, from_col), (to_row, to_col))

            # 更新状态
            score_text = f"评分: {score:.3f}" if score is not None else "评分: N/A"
            self.update_status(f"AI走法: {move_str} | {score_text}", fg='green')

        except Exception as e:
            print(f"[ERROR] 执行AI走法失败: {e}")
            self.update_status(f"走法错误: {str(e)}", fg='red')

    def board_to_fen(self):
        """将棋盘转换为FEN格式"""
        fen_rows = []
        for row in range(8):
            fen_row = ''
            empty_count = 0
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += piece
                else:
                    empty_count += 1
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)

        fen = '/'.join(fen_rows)
        turn = 'w' if self.is_white_turn else 'b'
        castling = 'KQkq'  # 简化，假设都可以易位
        return f"{fen} {turn} {castling} - 0 1"

    def send_cmd(self, cmd):
        """发送命令到ESP32（带延迟避免字符丢失）"""
        if not self.ser:
            return
        for char in cmd:
            self.ser.write(char.encode())
            time.sleep(0.01)
        self.ser.write(b'\n')
        time.sleep(0.1)

    def receive_from_esp32(self):
        """从ESP32接收数据"""
        while True:
            try:
                with self.serial_lock:  # 使用锁保护串口
                    if self.ser and self.ser.in_waiting:
                        data = self.ser.read_all().decode('utf-8', errors='ignore')
                        if 'Evaluation:' in data:
                            # 解析评估值
                            for line in data.split('\n'):
                                if 'Evaluation:' in line:
                                    try:
                                        eval_value = float(line.split('Evaluation:')[1].split()[0])
                                        self.root.after(0, lambda ev=eval_value: self.eval_label.config(text=f"评估: {ev:.3f}"))
                                    except:
                                        pass
            except:
                pass
            time.sleep(0.1)

    def update_status(self, message, fg='orange'):
        """更新状态标签"""
        self.status_label.config(text=message, fg=fg)

    def evaluate_position(self):
        """评估当前局面"""
        if not self.ser:
            messagebox.showerror("错误", "ESP32未连接")
            return

        fen = self.board_to_fen()
        self.status_label.config(text="评估中...", fg='orange')
        self.send_cmd(f"eval {fen}")
        self.status_label.config(text="就绪", fg='green')

    def get_ai_move(self):
        """获取AI走法"""
        if not self.ser:
            messagebox.showerror("错误", "ESP32未连接！\n请确保ESP32已烧录固件并连接到COM19")
            return

        if self.ai_thinking:
            return

        fen = self.board_to_fen()
        print(f"[DEBUG] get_ai_move called, FEN: {fen}")
        self.ai_thinking = True
        self.status_label.config(text="AI思考中（5-10秒）...", fg='orange')

        # 在后台线程中获取AI走法
        def get_move_thread():
            try:
                self.ai_thinking = True
                self.update_status(f"AI思考中... (预计10秒)")

                # 清空缓冲区
                if self.ser and self.ser.in_waiting > 0:
                    self.ser.read_all()

                # 发送命令（带延迟）
                cmd = f"bestmove {fen}"
                print(f"[DEBUG] 发送命令: {cmd.strip()}")
                for char in cmd:
                    self.ser.write(char.encode())
                    time.sleep(0.01)
                self.ser.write(b'\n')
                time.sleep(0.1)

                # 等待ESP32响应（15秒超时）
                response = ""
                for i in range(15):
                    time.sleep(1)
                    if self.ser and self.ser.in_waiting > 0:
                        data = self.ser.read_all().decode('utf-8', errors='ignore')
                        response += data
                        print(f"[DEBUG] 第{i+1}秒: 收到 {len(data)} 字节，总计 {len(response)} 字节")

                        # 检查是否收到完整的bestmove响应
                        if 'Best move:' in response and response.count(':') >= 2:
                            break

                print(f"[DEBUG] 完整响应:\n{response}")

                # 解析响应
                if 'Best move:' in response:
                    for line in response.split('\n'):
                        if 'Best move:' in line:
                            try:
                                move = line.split('Best move:')[1].strip()
                                # 只取前4个字符（走法部分）
                                move = move[:4] if len(move) >= 4 else move
                                print(f"[DEBUG] 解析到走法: {move}")

                                # 解析评分
                                score = None
                                if 'Score:' in response:
                                    for score_line in response.split('\n'):
                                        if 'Score:' in score_line:
                                            score = float(score_line.split('Score:')[1].strip())
                                            break

                                self.root.after(0, lambda m=move, s=score: self.make_ai_move(m, s))
                                return
                            except Exception as e:
                                print(f"[ERROR] 解析走法失败: {e}")
                                self.root.after(0, lambda: self.update_status(f"解析失败: {str(e)}"))
                                return

                # 未收到响应
                print("[ERROR] 未收到bestmove响应")
                self.root.after(0, lambda: self.update_status("未返回走法"))

            except Exception as e:
                print(f"[ERROR] 获取走法异常: {e}")
                self.root.after(0, lambda: self.update_status(f"错误: {str(e)}"))
            finally:
                self.ai_thinking = False

        threading.Thread(target=get_move_thread, daemon=True).start()

    def check_game_over(self):
        """检查游戏是否结束（简化版）"""
        # 检查王是否被吃掉
        white_king = any('K' in row for row in self.board)
        black_king = any('k' in row for row in self.board)

        if not white_king:
            messagebox.showinfo("游戏结束", "黑方获胜！")
            self.new_game()
        elif not black_king:
            messagebox.showinfo("游戏结束", "白方获胜！")
            self.new_game()

    def toggle_ai_mode(self):
        """切换AI模式"""
        self.ai_mode = not self.ai_mode
        mode_text = "开" if self.ai_mode else "关"
        self.status_label.config(text=f"AI模式: {mode_text}", fg='green')

        # 如果AI模式开启且轮到黑方，自动走棋
        if self.ai_mode and not self.is_white_turn and not self.ai_thinking:
            self.root.after(500, self.get_ai_move)

    def new_game(self):
        """新游戏"""
        self.board = self.create_initial_board()
        self.selected_square = None
        self.valid_moves = []
        self.last_move = None
        self.is_white_turn = True
        self.ai_thinking = False
        self.update_board()
        self.eval_label.config(text="评估: 0.00")
        self.status_label.config(text="就绪", fg='green')

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()