"""
国际象棋走法生成器
支持所有标准走法规则，包括王车易位和过路兵
"""

import chess

class ChessMoveGenerator:
    """国际象棋走法生成器"""
    
    def __init__(self, fen=None):
        """初始化棋盘"""
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()
    
    def generate_legal_moves(self):
        """生成所有合法走法（UCI格式）"""
        return [move.uci() for move in self.board.legal_moves]
    
    def generate_pseudo_legal_moves(self):
        """生成所有伪合法走法（不考虑王的安全）"""
        return [move.uci() for move in self.board.pseudo_legal_moves]
    
    def make_move(self, move_uci):
        """执行走法"""
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            return False
        except:
            return False
    
    def undo_move(self):
        """撤销走法"""
        self.board.pop()
    
    def is_check(self):
        """是否将军"""
        return self.board.is_check()
    
    def is_checkmate(self):
        """是否将死"""
        return self.board.is_checkmate()
    
    def is_stalemate(self):
        """是否逼和"""
        return self.board.is_stalemate()
    
    def is_draw(self):
        """是否和棋"""
        return self.board.is_draw()
    
    def get_board_fen(self):
        """获取FEN字符串"""
        return self.board.fen()
    
    def get_piece_at(self, square):
        """获取指定位置的棋子"""
        piece = self.board.piece_at(square)
        if piece:
            return piece.symbol()
        return None
    
    def get_turn(self):
        """获取当前回合"""
        return 'white' if self.board.turn == chess.WHITE else 'black'
    
    def get_castling_rights(self):
        """获取王车易位权限"""
        rights = []
        if self.board.has_kingside_castling_rights(chess.WHITE):
            rights.append('K')
        if self.board.has_queenside_castling_rights(chess.WHITE):
            rights.append('Q')
        if self.board.has_kingside_castling_rights(chess.BLACK):
            rights.append('k')
        if self.board.has_queenside_castling_rights(chess.BLACK):
            rights.append('q')
        return ''.join(rights) if rights else '-'
    
    def get_en_passant_square(self):
        """获取过路兵目标格"""
        ep_square = self.board.ep_square
        return chess.square_name(ep_square) if ep_square else '-'
    
    def get_halfmove_clock(self):
        """获取半回合计数"""
        return self.board.halfmove_clock
    
    def get_fullmove_number(self):
        """获取回合数"""
        return self.board.fullmove_number


def test_move_generator():
    """测试走法生成器"""
    print("="*50)
    print("测试走法生成器")
    print("="*50)
    
    # 测试1: 起始位置
    print("\n测试1: 起始位置")
    gen = ChessMoveGenerator()
    moves = gen.generate_legal_moves()
    print(f"FEN: {gen.get_board_fen()}")
    print(f"合法走法数量: {len(moves)}")
    print(f"走法: {moves[:10]}...")  # 只显示前10个
    
    # 测试2: 意大利开局
    print("\n测试2: 意大利开局")
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    gen = ChessMoveGenerator(fen)
    moves = gen.generate_legal_moves()
    print(f"FEN: {fen}")
    print(f"合法走法数量: {len(moves)}")
    print(f"走法: {moves[:10]}...")
    
    # 测试3: 执行走法
    print("\n测试3: 执行走法")
    gen = ChessMoveGenerator()
    print(f"初始FEN: {gen.get_board_fen()}")
    
    # 执行e2e4
    success = gen.make_move("e2e4")
    print(f"执行e2e4: {'成功' if success else '失败'}")
    print(f"新FEN: {gen.get_board_fen()}")
    
    # 执行e7e5
    success = gen.make_move("e7e5")
    print(f"执行e7e5: {'成功' if success else '失败'}")
    print(f"新FEN: {gen.get_board_fen()}")
    
    # 测试4: 王车易位
    print("\n测试4: 王车易位准备")
    # 设置一个可以王车易位的局面
    fen = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"
    gen = ChessMoveGenerator(fen)
    moves = gen.generate_legal_moves()
    print(f"FEN: {fen}")
    print(f"合法走法数量: {len(moves)}")
    castling_moves = [m for m in moves if m in ['e1g1', 'e1c1']]
    print(f"王车易位走法: {castling_moves}")
    
    # 测试5: 过路兵
    print("\n测试5: 过路兵")
    fen = "rnbqkbnr/pp1p1ppp/8/2pPp3/8/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 3"
    gen = ChessMoveGenerator(fen)
    moves = gen.generate_legal_moves()
    print(f"FEN: {fen}")
    print(f"合法走法数量: {len(moves)}")
    en_passant_moves = [m for m in moves if 'x' in m or len(m) == 4]
    print(f"可能包含过路兵的走法: {en_passant_moves[:10]}...")
    
    # 测试6: 将军检测
    print("\n测试6: 将军检测")
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    gen = ChessMoveGenerator(fen)
    # 执行一个将军的走法
    gen.make_move("e2e4")
    gen.make_move("e7e5")
    gen.make_move("f1c4")
    gen.make_move("f8c5")
    gen.make_move("d1h5")  # 后h5，黑方被将军
    print(f"是否将军: {gen.is_check()}")
    print(f"FEN: {gen.get_board_fen()}")
    
    print("\n" + "="*50)
    print("测试完成!")
    print("="*50)


if __name__ == "__main__":
    test_move_generator()