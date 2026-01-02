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
    print("Test 1: Starting Position")
    print("="*50)

    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    # Use python-chess
    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    # Use our move generator
    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess moves: {len(py_moves)}")
    print(f"Our moves: {len(my_moves)}")
    print(f"Moves: {my_moves[:10]}...")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("[OK] Test passed! Moves match perfectly")
    else:
        print("[FAIL] Test failed!")
        if missing:
            print(f"Missing moves: {missing}")
        if extra:
            print(f"Extra moves: {extra}")

    print()
    return match

def test_italian_game():
    """测试意大利开局"""
    print("="*50)
    print("Test 2: Italian Game")
    print("="*50)

    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess moves: {len(py_moves)}")
    print(f"Our moves: {len(my_moves)}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("[OK] Test passed! Moves match perfectly")
    else:
        print("[FAIL] Test failed!")
        if missing:
            print(f"Missing moves: {missing}")
        if extra:
            print(f"Extra moves: {extra}")

    print()
    return match

def test_castling():
    """测试王车易位"""
    print("="*50)
    print("Test 3: Castling")
    print("="*50)

    fen = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess moves: {len(py_moves)}")
    print(f"Our moves: {len(my_moves)}")

    # Check castling moves
    castling_moves = [m for m in my_moves if m in ['e1g1', 'e1c1']]
    print(f"Castling moves: {castling_moves}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("[OK] Test passed! Moves match perfectly")
    else:
        print("[FAIL] Test failed!")
        if missing:
            print(f"Missing moves: {missing}")
        if extra:
            print(f"Extra moves: {extra}")

    print()
    return match

def test_en_passant():
    """测试过路兵"""
    print("="*50)
    print("Test 4: En Passant")
    print("="*50)

    fen = "rnbqkbnr/pp1p1ppp/8/2pPp3/8/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 3"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"python-chess moves: {len(py_moves)}")
    print(f"Our moves: {len(my_moves)}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("[OK] Test passed! Moves match perfectly")
    else:
        print("[FAIL] Test failed!")
        if missing:
            print(f"Missing moves: {missing}")
        if extra:
            print(f"Extra moves: {extra}")

    print()
    return match

def test_check():
    """测试将军"""
    print("="*50)
    print("Test 5: Check")
    print("="*50)

    fen = "rnbqkbnr/pppp1ppp/8/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"

    board = chess.Board(fen)
    py_moves = [move.uci() for move in board.legal_moves]

    gen = ChessMoveGenerator(fen)
    my_moves = gen.generate_legal_moves()

    print(f"FEN: {fen}")
    print(f"In check: {gen.is_check()}")
    print(f"python-chess moves: {len(py_moves)}")
    print(f"Our moves: {len(my_moves)}")

    match, missing, extra = compare_moves(my_moves, py_moves)
    if match:
        print("[OK] Test passed! Moves match perfectly")
    else:
        print("[FAIL] Test failed!")
        if missing:
            print(f"Missing moves: {missing}")
        if extra:
            print(f"Extra moves: {extra}")

    print()
    return match

def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("="*50)
    print("Starting Move Generator Tests")
    print("="*50)
    print("\n")

    results = []
    results.append(("Starting Position", test_starting_position()))
    results.append(("Italian Game", test_italian_game()))
    results.append(("Castling", test_castling()))
    results.append(("En Passant", test_en_passant()))
    results.append(("Check", test_check()))

    print("\n")
    print("="*50)
    print("Test Summary")
    print("="*50)
    print("\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] Passed" if result else "[FAIL] Failed"
        print(f"{name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\nAll tests passed! Move generator works correctly!")
    else:
        print(f"\n{total - passed} tests failed, need to fix")

    return passed == total

if __name__ == "__main__":
    run_all_tests()
