import unittest
import chess
from src.eval import check_end_game, evaluate_piece, evaluate_capture, move_value


class EvalTest(unittest.TestCase):
    def setUp(self):
        self.board = chess.Board()

    ## evaluate_piece()
    # NORMAL
    def test_piece_evaluation_with_piece(self):
        self.board.reset()
        piece = chess.Piece(chess.PAWN, chess.WHITE)
        score = evaluate_piece(piece, chess.A1, False)
        print("test_piece_evaluation_with_piece: A1 PAWN VALUE", score)
        self.assertIsNotNone(score, "Score should not be None when a piece is present")

    # FURTHER - KNIGHT
    def test_knight_central_vs_peripheral(self):
        # Place a knight on a central square and evaluate
        central_knight_square = chess.E4
        self.board.set_piece_at(central_knight_square, chess.Piece(chess.KNIGHT, chess.WHITE))
        central_value = evaluate_piece(self.board.piece_at(central_knight_square), central_knight_square, False)

        # Place a knight on a peripheral square and evaluate
        peripheral_knight_square = chess.A1
        self.board.set_piece_at(peripheral_knight_square, chess.Piece(chess.KNIGHT, chess.WHITE))
        peripheral_value = evaluate_piece(self.board.piece_at(peripheral_knight_square), peripheral_knight_square,
                                          False)

        # Assert that the central square has a higher value
        self.assertTrue(central_value > peripheral_value,
                        "Knight on central square should have a higher value than on a peripheral square")

    # FURTHER - BISHOP
    def test_bishop_central_vs_peripheral(self):
        # Place a bishop on a central square and evaluate
        central_bishop_square = chess.D4
        self.board.set_piece_at(central_bishop_square, chess.Piece(chess.BISHOP, chess.WHITE))
        central_value = evaluate_piece(self.board.piece_at(central_bishop_square), central_bishop_square, False)

    # INVALID
    def test_piece_evaluation_no_piece(self):
        self.board.reset()
        score = evaluate_piece(None, chess.A1, False)
        self.assertIsNone(score, "Score should be None when no piece is present")

    ## check_end_game()
    # NORMAL
    def test_end_game_check(self):
        # End-game setup
        self.board.clear_board()
        self.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        self.board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        self.assertTrue(check_end_game(self.board), "End-game state")

    # INVALID
    def test_end_game_check_with_queens(self):
        self.board.reset()
        # default setup should not be in endgame
        self.assertTrue(check_end_game(self.board), "Endgame is false when queens are present")

    # BOUNDARY
    def test_end_game_check_pawns_and_minor_pieces(self):
        self.board.reset()
        self.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        self.board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        self.board.set_piece_at(chess.A2, chess.Piece(chess.PAWN, chess.WHITE))
        self.assertFalse(check_end_game(self.board), "Endgame should be true with additional pawns on the board")

    ## evaluate_capture()
    # NORMAL
    def test_capture_evaluation_normal_capture(self):
        self.board.reset()
        self.board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.WHITE))
        self.board.set_piece_at(chess.D6, chess.Piece(chess.KNIGHT, chess.BLACK))
        move = chess.Move.from_uci('e5d6')
        value = evaluate_capture(self.board, move)
        print("test_capture_evaluation_normal_capture: e5d6 value", value)
        self.assertIsInstance(value, int, "Value should be an int for a normal capture")

    # FURTHER/BOUNDARY
    def test_capture_evaluation_en_passant(self):
        # en passant FEN
        self.board.set_fen("8/8/8/5Pp1/8/8/8/8 w - g6 0 2")
        move = chess.Move.from_uci('f5g6')
        value = evaluate_capture(self.board, move)
        print("test_capture_evaluation_en_passant: f5g6 value", value)
        self.assertIsInstance(value, int, "En passant failure: Value should be an int for en passant capture")
        self.assertTrue(value > 0, "En passant failure: Value should be positive for en passant capture")

    # INVALID
    def test_capture_evaluation_no_piece(self):
        self.board.reset()
        move = chess.Move.from_uci('e5d6')
        value = evaluate_capture(self.board, move)
        self.assertIsNone(value, "Value should be None when no piece is present")

    ## move_value()
    # NORMAL
    def test_move_value_calculation(self):
        # Evaluate pawn promotion
        self.board.set_piece_at(chess.C1, chess.Piece(chess.BISHOP, chess.WHITE))
        self.board.set_piece_at(chess.A8, chess.Piece(chess.ROOK, chess.BLACK))
        move = chess.Move.from_uci('c1g5')
        value = move_value(self.board, move, False)  # for this test, we are not in the end-game
        print("test_move_value_calculation: c1g5 value", value)
        self.assertTrue(value > 0, "Value should be positive")
        print(value)

    # BOUNDARY
    def test_move_value_resulting_in_checkmate(self):
        self.board.set_fen("7k/5PPP/8/8/8/8/8/7K w - - 0 1")
        move = chess.Move.from_uci('g7g8q')  # Pawn to g8 with promotion to Queen, assuming this syntax is correct
        value = move_value(self.board, move, False)
        print("test_move_value_resulting_in_checkmate: CHECKMATE VALUE", value)
        self.assertTrue(value > 100, "Value should be extremely high (+inf) due to checkmate")


if __name__ == '__main__':
    unittest.main()
