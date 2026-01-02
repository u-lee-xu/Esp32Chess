"""
测试走法生成器功能
验证所有棋子的走法规则
"""

import chess
from movegen import ChessMoveGenerator

def compare_moves(my_moves, python_moves):
    """比较两个走法列表"""
    my_set = set(my_moves)
    py_set = set(python_moves)

    missing = py_set - my_set
    extra = my_set - py_set

    return len(missing) == 0 and len(extra) == 0, missing, extra

def test_starting_position():
    """测试起始位置"""
    print("="*50)
    print("测试1: 起始位置")
    print("="*50)

    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    # 使用python-chess
    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    # 使用我们的走法生成器
    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess走法数: {len(py_moves)}")
    print(f"我们的走法数: {len(my_moves)}")
    print(f"走法: {my_moves[:10]}...")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("✅ 测试通过！走法完全一致")
    else:
        print("❌ 测试失败！")
        if missing:
            print(f"缺失的走法: {missing}")
        if extra:
            print(f"多余的走法: {extra}")

    print()
    return match

def test_italian_game():
    """测试意大利开局"""
    print("="*50)
    print("测试2: 意大利开局")
    print("="*50)

    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess走法数: {len(py_moves)}")
    print(f"我们的走法数: {len(my_moves)}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("✅ 测试通过！走法完全一致")
    else:
        print("❌ 测试失败！")
        if missing:
            print(f"缺失的走法: {missing}")
        if extra:
            print(f"多余的走法: {extra}")

    print()
    return match

def test_castling():
    """测试王车易位"""
    print("="*50)
    print("测试3: 王车易位")
    print("="*50)

    fen = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess走法数: {len(py_moves)}")
    print(f"我们的走法数: {len(my_moves)}")

    # 检查王车易位走法
    castling_moves = [m for m in my_moves if m in ['e1g1', 'e1c1']]
    print(f"王车易位走法: {castling_moves}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("✅ 测试通过！走法完全一致")
    else:
        print("❌ 测试失败！")
        if missing:
            print(f"缺失的走法: {missing}")
        if extra:
            print(f"多余的走法: {extra}")

    print()
    return match

def test_en_passant():
    """测试过路兵"""
    print("="*50)
    print("测试4: 过路兵")
    print("="*50)

    fen = "rnbqkbnr/pp1p1ppp/8/2pPp3/8/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 3"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess走法数: {len(py_moves)}")
    print(f"我们的走法数: {len(my_moves)}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("✅ 测试通过！走法完全一致")
    else:
        print("❌ 测试失败！")
        if missing:
            print(f"缺失的走法: {missing}")
        if extra:
            print(f"多余的走法: {extra}")

    print()
    return match

def test_promotion():
    """测试兵升变"""
    print("="*50)
    print("测试5: 兵升变")
    print("="*50)

    fen = "r1bqkbnr/pppp1ppp/8/4p3/8/8/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
    # 模拟走到兵可以升变的位置
    board = chess.Board(fen)
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("f4")
    board.push_san("exf4")
    board.push_san("g4")
    board.push_san("fxg3")
    board.push_san("h4")
    board.push_san("gxh2")
    board.push_san("hxg5")
    board.push_san("hxg6")
    board.push_san("gxh7")
    board.push_san("hxg8")  # 升变

    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(board.fen())
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {board.fen()}")
    print(f"python-chess走法数: {len(py_moves)}")
    print(f"我们的走法数: {len(my_moves)}")

    # 检查升变走法
    promotion_moves = [m for m in my_moves if len(m) == 5]
    print(f"升变走法: {promotion_moves}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("✅ 测试通过！走法完全一致")
    else:
        print("❌ 测试失败！")
        if missing:
            print(f"缺失的走法: {missing}")
        if extra:
            print(f"多余的走法: {extra}")

    print()
    return match

def test_check():
    """测试将军"""
    print("="*50)
    print("测试6: 将军")
    print("="*50)

    # 创建一个将军的局面
    fen = "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"是否将军: {gen.is_check()}")
    print(f"python-chess走法数: {len(py_moves)}")
    print(f"我们的走法数: {len(my_moves)}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("✅ 测试通过！走法完全一致")
    else:
        print("❌ 测试失败！")
        if missing:
            print(f"缺失的走法: {missing}")
        if extra:
            print(f"多余的走法: {extra}")

    print()
    return match

def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("="*50)
    print("开始走法生成器测试")
    print("="*50)
    print("\n")

    results = []
    results.append(("起始位置", test_starting_position()))
    results.append(("意大利开局", test_italian_game()))
    results.append(("王车易位", test_castling()))
    results.append(("过路兵", test_en_passant()))
    results.append(("兵升变", test_promotion()))
    results.append(("将军", test_check()))

    print("\n")
    print("="*50)
    print("测试总结")
    print("="*50)
    print("\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！走法生成器工作正常！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，需要修复")

    return passed == total

if __name__ == "__main__":
    run_all_tests()
