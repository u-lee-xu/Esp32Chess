# -*- coding: utf-8 -*-
"""
使用Stockfish为PGN对局生成位置评估值
将评估值添加到训练数据中
"""

import json
import chess.pgn
import subprocess
import time
import os
from pathlib import Path

class StockfishEvaluator:
    def __init__(self, stockfish_path=r"C:\Users\Mia\Documents\esp32chess\stockfish\stockfish\stockfish-windows-x86-64-avx2.exe"):
        """初始化Stockfish评估器"""
        self.stockfish_path = stockfish_path
        self.process = None
        self.depth = 15  # 评估深度（15-20之间平衡速度和质量）

    def start(self):
        """启动Stockfish进程"""
        try:
            self.process = subprocess.Popen(
                [self.stockfish_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 初始化UCI
            self.send_command("uci")
            self.wait_for_response("uciok")
            self.send_command("setoption name MultiPV value 1")

            print("[OK] Stockfish started successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start Stockfish: {e}")
            return False

    def send_command(self, command):
        """发送命令到Stockfish"""
        if self.process:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    def wait_for_response(self, expected_text, timeout=30):
        """等待Stockfish响应"""
        start_time = time.time()
        response_lines = []

        while time.time() - start_time < timeout:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    response_lines.append(line)
                    if expected_text in line:
                        return response_lines
            except:
                pass

        return response_lines

    def evaluate_position(self, fen, depth=None):
        """评估单个棋盘位置"""
        if not self.process:
            return None

        eval_depth = depth or self.depth

        # 设置位置
        self.send_command(f"position fen {fen}")

        # 开始分析
        self.send_command(f"go depth {eval_depth}")

        # 等待结果
        start_time = time.time()
        eval_score = None

        while time.time() - start_time < 60:  # 60秒超时
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if line.startswith("info") and "score" in line:
                        # 解析评估值
                        eval_score = self.parse_evaluation(line)
                        # 不立即返回，继续等待更深的结果
                    elif line.startswith("bestmove"):
                        # 分析完成
                        break
            except Exception as e:
                print(f"[ERROR] Reading Stockfish output: {e}")
                break

        return eval_score

    def parse_evaluation(self, info_line):
        """从Stockfish输出中解析评估值"""
        try:
            # 示例: info depth 15 seldepth 29 score cp 50 ...
            # 或: info depth 15 seldepth 29 score mate 3 ...
            parts = info_line.split()

            score_index = parts.index("score")
            score_type = parts[score_index + 1]
            score_value = int(parts[score_index + 2])

            if score_type == "cp":
                # centipawn评估，转换为-1到1范围
                # 通常 +/-1000cp约为 +/-10分兵，对应 +/-1
                eval_score = score_value / 1000.0
                # 限制在-1到1之间
                eval_score = max(-1.0, min(1.0, eval_score))
                return eval_score
            elif score_type == "mate":
                # 将杀评估，转换为接近-1或1的值
                if score_value > 0:
                    return 0.9  # 白方即将获胜
                else:
                    return -0.9  # 黑方即将获胜
        except:
            pass

        return None

    def stop(self):
        """停止Stockfish进程"""
        if self.process:
            self.send_command("quit")
            self.process.terminate()
            self.process = None
            print("[OK] Stockfish stopped")


def process_pgn_file(pgn_file, output_file, max_games=None, max_positions_per_game=50):
    """处理PGN文件，为所有位置生成评估值"""
    print(f"\nProcessing PGN file: {pgn_file}")
    print(f"Output file: {output_file}")
    print(f"Max games: {max_games or 'all'}")
    print(f"Max positions per game: {max_positions_per_game}")
    print()

    # 初始化Stockfish
    evaluator = StockfishEvaluator()
    if not evaluator.start():
        print("[ERROR] Failed to start Stockfish. Please install Stockfish first.")
        print("\nInstallation instructions:")
        print("1. Download from: https://stockfishchess.org/download")
        print("2. Extract to a folder")
        print("3. Add to PATH or specify path in script")
        return

    # 读取PGN文件
    with open(pgn_file, 'r', encoding='utf-8') as f:
        games_processed = 0
        positions_processed = 0
        all_samples = []

        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break

            if max_games and games_processed >= max_games:
                break

            # 提取位置和走法
            board = game.board()
            node = game
            game_samples = []
            positions_in_game = 0

            while node.variations and positions_in_game < max_positions_per_game:
                node = node.variations[0]  # 主变体

                # 评估当前位置
                fen = board.fen()
                eval_score = evaluator.evaluate_position(fen)

                if eval_score is not None:
                    # 将棋盘转换为张量
                    board_tensor = board_to_tensor(board)

                    # 获取对局结果
                    result = game.headers.get('Result', '*')
                    result_map = {'1-0': 1.0, '0-1': -1.0, '1/2-1/2': 0.0, '*': 0.0}
                    game_result = result_map.get(result, 0.0)

                    # 保存样本
                    sample = {
                        'board_state': board_tensor.tolist(),
                        'move': node.move.uci(),
                        'eval': float(eval_score),  # 使用Stockfish评估
                        'result': float(game_result)
                    }
                    game_samples.append(sample)
                    positions_in_game += 1

                # 推进棋盘
                board.push(node.move)

            all_samples.extend(game_samples)
            games_processed += 1
            positions_processed += positions_in_game

            # 进度报告
            if games_processed % 10 == 0:
                print(f"Processed {games_processed} games, {positions_processed} positions...")

    # 保存结果
    print(f"\nSaving {len(all_samples)} samples to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_samples, f, indent=2)

    print(f"[OK] Saved {len(all_samples)} samples")
    print(f"  Games processed: {games_processed}")
    print(f"  Positions evaluated: {positions_processed}")

    # 停止Stockfish
    evaluator.stop()


def board_to_tensor(board):
    """将棋盘状态转换为8x8x12的张量"""
    import numpy as np

    tensor = np.zeros((8, 8, 12), dtype=np.float32)

    piece_to_index = {
        'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
        'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = square // 8
            col = square % 8
            piece_char = piece.symbol()
            tensor[row, col, piece_to_index[piece_char]] = 1.0

    return tensor


def main():
    print("=" * 80)
    print("Stockfish Evaluation Generator")
    print("=" * 80)
    print()

    # 配置
    pgn_file = "lichess_tournament_2025.12.31_C5W0R90y_hourly-ultrabullet.pgn"
    output_file = "chess_training_data_with_eval.json"

    # 检查文件是否存在
    if not os.path.exists(pgn_file):
        print(f"[ERROR] PGN file not found: {pgn_file}")
        return

    # 处理PGN文件
    # 注意：评估所有位置会很慢，建议先用少量游戏测试
    process_pgn_file(
        pgn_file,
        output_file,
        max_games=500,  # 处理所有500局对局
        max_positions_per_game=50  # 每局最多50个位置
    )

    print("\n" + "=" * 80)
    print("Evaluation generation complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review the generated data: chess_training_data_with_eval.json")
    print("2. Train the model with: python train_model.py")
    print("3. Test the model with: python test_model.py")


if __name__ == "__main__":
    main()