"""
PGN数据解析器 - 为ESP32国际象棋AI准备训练数据
支持提取棋盘状态、走法、评估值等信息
"""

import chess.pgn
import numpy as np
import json
from pathlib import Path


class ChessDataExtractor:
    def __init__(self, pgn_file):
        self.pgn_file = pgn_file
        self.games = []

    def parse_pgn(self, max_games=None, variant_filter=None):
        """解析PGN文件，提取对局数据"""
        with open(self.pgn_file, 'r', encoding='utf-8') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break

                # 过滤变体
                if variant_filter:
                    headers = game.headers
                    variant = headers.get('Variant', 'Standard')
                    if variant != variant_filter:
                        continue

                self.games.append(game)
                if max_games and len(self.games) >= max_games:
                    break

        print(f"成功解析 {len(self.games)} 局对局")
        return self.games

    def extract_training_samples(self, game, max_samples_per_game=100):
        """
        从单个对局中提取训练样本
        返回: (board_state, move, eval_score, result)
        """
        samples = []
        board = game.board()
        node = game

        # 获取对局结果
        result = game.headers.get('Result', '*')
        result_map = {'1-0': 1.0, '0-1': -1.0, '1/2-1/2': 0.0, '*': 0.0}
        game_result = result_map.get(result, 0.0)

        sample_count = 0
        while node.variations and sample_count < max_samples_per_game:
            node = node.variations[0]  # 获取主变体
            move = node.move

            # 获取评估值（如果有）
            eval_score = 0.0
            if node.comment:
                # 尝试从注释中提取评估值
                comment = node.comment
                if '[%eval' in comment:
                    try:
                        eval_str = comment.split('[%eval')[1].split(']')[0].strip()
                        eval_score = float(eval_str)
                    except:
                        pass

            # 提取棋盘状态（8x8x12的one-hot编码）
            board_state = self.board_to_tensor(board)

            # 将走法转换为索引
            move_index = self.move_to_index(move, board)

            samples.append({
                'board_state': board_state,
                'move': move_index,
                'eval': eval_score,
                'result': game_result
            })

            board.push(move)
            sample_count += 1

        return samples

    def board_to_tensor(self, board):
        """将棋盘状态转换为8x8x12的张量"""
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

    def move_to_index(self, move, board):
        """将走法转换为索引（简化版，实际需要更复杂的编码）"""
        # 简化处理：返回走法的UCI表示
        return move.uci()

    def export_to_json(self, output_file, max_samples=10000):
        """导出训练数据到JSON文件"""
        all_samples = []
        sample_count = 0

        for game in self.games:
            samples = self.extract_training_samples(game)
            all_samples.extend(samples)
            sample_count += len(samples)

            if sample_count >= max_samples:
                break

        print(f"提取了 {len(all_samples)} 个训练样本")

        # 转换为可序列化的格式
        export_data = []
        for sample in all_samples:
            export_data.append({
                'board_state': sample['board_state'].tolist(),
                'move': sample['move'],
                'eval': float(sample['eval']),
                'result': float(sample['result'])
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        print(f"数据已保存到 {output_file}")
        return export_data


def main():
    # 配置
    pgn_file = "lichess_tournament_2025.12.31_C5W0R90y_hourly-ultrabullet.pgn"
    output_file = "chess_training_data.json"

    print(f"开始解析 {pgn_file}...")

    # 创建解析器
    extractor = ChessDataExtractor(pgn_file)

    # 解析PGN（只解析标准国际象棋对局）
    extractor.parse_pgn(max_games=500)  # 解析500局

    # 导出训练数据
    extractor.export_to_json(output_file, max_samples=20000)

    print("\n数据准备完成！")


if __name__ == "__main__":
    main()
