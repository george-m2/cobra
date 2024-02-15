import unittest
import chess
from eval import check_end_game, evaluate_piece, evaluate_capture, move_value


class EvalTest(unittest.TestCase):
    def setUp(self):
        self.board = chess.Board()

    def test_end_game_check(self):
        # End-game setup
        self.board.clear_board()
        self.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        self.board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        self.assertTrue(check_end_game(self.board), "End-game state")

    def test_piece_evaluation(self):
        # White knight - G1
        self.board.set_piece_at(chess.G1, chess.Piece(chess.KNIGHT, chess.WHITE))
        is_end_game = check_end_game(self.board)
        score = evaluate_piece(chess.Piece(chess.KNIGHT, chess.WHITE), chess.G1, is_end_game)
        # Check that the score is an integer
        self.assertIsInstance(score, int, "Score should be an integer")

        # G1 Knight value in eval.py
        expected_score = -40

        self.assertEqual(score, expected_score,
                         f"Expected score for a knight on G1 to be {expected_score}, but got {score}")

    def test_capture_evaluation(self):
        # Evaluate capture
        temp_board = self.board.copy()
        temp_board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.WHITE))
        temp_board.set_piece_at(chess.D6, chess.Piece(chess.KNIGHT, chess.BLACK))
        move = chess.Move.from_uci('e5d6')
        print(temp_board.is_capture(move))
        value = evaluate_capture(temp_board, move)
        self.assertIsInstance(value, int, "Value should be an int")
        print(value)

    def test_move_value_calculation(self):
        # Evaluate pawn promotion
        self.board.set_piece_at(chess.C1, chess.Piece(chess.BISHOP, chess.WHITE))
        self.board.set_piece_at(chess.A8, chess.Piece(chess.ROOK, chess.BLACK))
        move = chess.Move.from_uci('c1g5')
        value = move_value(self.board, move, False) # for this test, we are not in the end-game
        self.assertTrue(value > 0, "Value should be positive")
        print(value)


if __name__ == '__main__':
    unittest.main()
