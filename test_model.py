# -*- coding: utf-8 -*-
"""
测试训练好的国际象棋AI模型
在PC上运行，验证模型功能
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import chess

def load_model(model_path):
    """加载训练好的模型"""
    print(f"正在加载模型: {model_path}")
    model = keras.models.load_model(model_path)
    print(f"[OK] 模型加载成功")
    print(f"  参数数量: {model.count_params():,}")
    return model

def fen_to_tensor(fen):
    """将FEN字符串转换为8x8x12的张量"""
    board = chess.Board(fen)
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

def evaluate_position(model, fen):
    """评估棋盘位置"""
    tensor = fen_to_tensor(fen)
    tensor = np.expand_dims(tensor, axis=0)  # 添加batch维度

    prediction = model.predict(tensor, verbose=0)
    return float(prediction[0][0])

def print_board(fen):
    """打印棋盘"""
    board = chess.Board(fen)
    print(board)
    print()

def get_evaluation_text(eval_score):
    """将评估分数转换为文字描述"""
    if eval_score > 0.8:
        return "白方大优"
    elif eval_score > 0.4:
        return "白方优势"
    elif eval_score > 0.2:
        return "白方略优"
    elif eval_score > -0.2:
        return "均势"
    elif eval_score > -0.4:
        return "黑方略优"
    elif eval_score > -0.8:
        return "黑方优势"
    else:
        return "黑方大优"

def test_positions(model):
    """测试多个经典棋局位置"""

    test_cases = [
        {
            "name": "起始位置",
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "expected": "均势"
        },
        {
            "name": "意大利开局",
            "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
            "expected": "白方略优"
        },
        {
            "name": "西西里防御",
            "fen": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
            "expected": "均势"
        },
        {
            "name": "王翼弃兵",
            "fen": "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2",
            "expected": "白方略优"
        },
        {
            "name": "后翼弃兵",
            "fen": "rnbqkbnr/pp1ppppp/8/2p5/8/2PP4/PP2PPPP/RNBQKBNR w KQkq c6 0 2",
            "expected": "均势"
        },
        {
            "name": "西班牙开局",
            "fen": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
            "expected": "白方略优"
        },
        {
            "name": "中局复杂局面",
            "fen": "r4rk1/pp2ppbp/2p3p1/8/2BP2n1/2N1P3/PP3PPP/R3KB1R w KQ - 0 12",
            "expected": "白方优势"
        },
        {
            "name": "白方进攻型局面",
            "fen": "r1b1r1k1/pp3ppp/2p5/3q4/3P4/2NQ1N2/PPP2PPP/R3KB1R w KQ - 0 15",
            "expected": "白方优势"
        },
        {
            "name": "黑方反击型局面",
            "fen": "r2q1rk1/pp3ppp/2p5/3p4/3P4/2NQ1N2/PPP2PPP/R3KB1R b KQ - 0 15",
            "expected": "黑方略优"
        },
        {
            "name": "残局 - 白方多兵",
            "fen": "8/8/8/8/8/4P3/3PK3/8 w - - 0 1",
            "expected": "白方大优"
        }
    ]

    print("=" * 80)
    print("开始测试棋局位置评估")
    print("=" * 80)
    print()

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"测试 {i}/{len(test_cases)}: {test['name']}")
        print("-" * 80)

        print(f"FEN: {test['fen']}")
        print()

        # 打印棋盘
        print_board(test['fen'])

        # 评估位置
        eval_score = evaluate_position(model, test['fen'])
        eval_text = get_evaluation_text(eval_score)

        print(f"评估分数: {eval_score:+.4f}")
        print(f"评估结果: {eval_text}")
        print(f"预期结果: {test['expected']}")
        print()

        # 检查是否符合预期
        if eval_text == test['expected']:
            print("[OK] 评估结果符合预期")
        else:
            print(f"[WARN] 评估结果与预期不符（预期：{test['expected']}）")

        print()
        print("=" * 80)
        print()

        results.append({
            "name": test['name'],
            "score": eval_score,
            "eval": eval_text,
            "expected": test['expected'],
            "match": eval_text == test['expected']
        })

    # 统计结果
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总测试数: {len(results)}")
    print(f"符合预期: {sum(1 for r in results if r['match'])}")
    print(f"不符合预期: {sum(1 for r in results if not r['match'])}")
    print()

    # 显示所有结果
    print("\n详细结果:")
    print("-" * 80)
    print(f"{'名称':<20} {'分数':>10} {'评估':<12} {'预期':<12} {'结果':<8}")
    print("-" * 80)
    for r in results:
        status = "OK" if r['match'] else "FAIL"
        print(f"{r['name']:<20} {r['score']:>+10.4f} {r['eval']:<12} {r['expected']:<12} {status:<8}")

def interactive_test(model):
    """交互式测试模式"""
    print("\n" + "=" * 80)
    print("交互式测试模式")
    print("=" * 80)
    print("输入FEN格式的棋局，输入 'quit' 退出")
    print()

    while True:
        fen = input("请输入FEN（或输入 'quit' 退出）: ").strip()

        if fen.lower() == 'quit':
            print("退出交互模式")
            break

        if not fen:
            continue

        try:
            # 验证FEN格式
            board = chess.Board(fen)

            print("\n棋盘:")
            print(board)
            print()

            # 评估
            eval_score = evaluate_position(model, fen)
            eval_text = get_evaluation_text(eval_score)

            print(f"评估分数: {eval_score:+.4f}")
            print(f"评估结果: {eval_text}")
            print()

        except ValueError as e:
            print(f"错误: 无效的FEN格式 - {e}")
            print()

def main():
    print("\n" + "=" * 80)
    print("国际象棋AI模型测试工具")
    print("=" * 80)
    print()

    # 加载模型
    model_path = "models/chess_ai_model.keras"
    model = load_model(model_path)

    # 运行测试
    test_positions(model)

    print("\n测试完成！")
    print("\n提示: 如需交互测试，请取消注释interactive_test(model)调用")

if __name__ == "__main__":
    main()