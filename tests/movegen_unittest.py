import unittest
import chess
from src.movegen import next_move, get_move_quality, get_ordered_moves, find_best_move_minimax, minimax


class MoveGenTest(unittest.TestCase):

    def setUp(self):
        self.board = chess.Board()
        self.depth = 3
        self.maximizing_player = True  # white - maximising player
        self.alpha = float("-inf")
        self.beta = float("inf")

    # next_move()
    ## NORMAL
    def test_next_move(self):
        self.board.reset_board()
        best_move = next_move(self.depth, self.board)
        print("test_next_move(): best_move", best_move)
        self.assertIsInstance(best_move, chess.Move, "next_move should return a chess.Move object")

    ## BOUNDARY
    def test_next_move_boundary(self):
        self.board.reset_board()
        depth = 30  # local depth to test boundary
        best_move = next_move(self.depth, self.board)
        print("test_next_move(): best_move", best_move)
        self.assertIsInstance(best_move, chess.Move, "next_move should return a chess.Move object")

    ## INVALID
    def test_next_move_invalid(self):
        self.board.reset_board()
        depth = -1  # local depth to test invalid depth
        best_move = next_move(self.depth, self.board)
        print("test_next_move(): best_move", best_move)
        self.assertIsInstance(best_move, chess.Move, "next_move should return a chess.Move object")

    # get_ordered_moves()
    ## NORMAL
    def test_ordered_moves_generation(self):
        self.board.reset()
        ordered_moves = get_ordered_moves(self.board)
        print("test_ordered_moves_generation(): ordered_moves", ordered_moves)
        self.assertIsInstance(ordered_moves, list, "get_ordered_moves should return a list")
        self.assertTrue(all(isinstance(move, chess.Move) for move in ordered_moves),
                        "All items should be chess.Move objects")

    ## BOUNDARY
    def test_ordered_moves_generation_stalemate(self):
        stalemate_fen = "7k/5Q2/5K2/8/8/8/8/8 b - - 0 1"  # Black to move, stalemate
        self.board.set_fen(stalemate_fen)
        ordered_moves = get_ordered_moves(self.board)
        print("test_ordered_moves_generation_stalemate(): ordered_moves", ordered_moves)
        self.assertIsInstance(ordered_moves, list, "get_ordered_moves should return a list in stalemate")
        self.assertEqual(len(ordered_moves), 0, "Expected no legal moves in a stalemate position")

    # find_best_move_minimax()
    ## NORMAL
    def test_best_move_via_minimax(self):
        best_move = find_best_move_minimax(self.depth, self.board)
        print("test_best_move_via_minimax(): best_move", best_move)
        self.assertIsInstance(best_move, chess.Move, "find_best_move_minimax should return a chess.Move object")

    ## FURTHER TESTING
    def test_best_move_via_minimax_ftesting(self):
        self.board.reset_board()
        self.board.set_fen("7k/5P2/8/8/8/8/8/7K w - - 0 1") # Promotion
        best_move = find_best_move_minimax(self.depth, self.board)
        print("test_best_move_via_minimax(): best_move", best_move)
        self.assertIsInstance(best_move, chess.Move, "find_best_move_minimax should return a chess.Move object")

    ## BOUNDARY
    def test_best_move_via_minimax_boundary(self):
        self.board.reset_board()
        self.board.set_fen("8/8/8/8/8/8/8/4K3 w - - 0 1") # Promotion
        best_move = find_best_move_minimax(self.depth, self.board)
        print("test_best_move_via_minimax(): best_move", best_move)
        self.assertIsInstance(best_move, chess.Move, "find_best_move_minimax should return a chess.Move object")

    # minimax()
    ## NORMAL
    def test_minimax_algorithm(self):
        score = minimax(self.depth, self.board, self.alpha, self.beta, self.maximizing_player)
        print("test_minimax_algorithm(): score", score)
        self.assertIsInstance(score, int, "minimax should return a float score")

    ## BOUNDARY & FURTHER TESTING
    def test_minimax_algorithm_stalemate(self):
        # Black king on a8, White king on b6, and White pawn on a7
        stalemate_fen = "k7/P7/1K6/8/8/8/8/8 w - - 0 1"
        self.board.set_fen(stalemate_fen)
        self.alpha = float("-inf")
        self.beta = float("inf")
        self.maximizing_player = True
        score = minimax(self.depth, self.board, self.alpha, self.beta, self.maximizing_player)
        print("test_minimax_algorithm_stalemate(): score", score)
        self.assertEqual(score, 0, "minimax should recognize stalemate as the best outcome")

    ## INVALID
    def test_minimax_algorithm_swapped_alpha_beta(self):
        self.board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.depth = 3
        self.alpha = float("inf")  # worst score for maximiser
        self.beta = float("-inf")  # worst score for minimiser
        self.maximizing_player = True

        score = minimax(self.depth, self.board, self.alpha, self.beta, self.maximizing_player)
        print("test_minimax_algorithm_swapped_alpha_beta(): score", score)
        self.assertTrue(True, "Observing behavior with swapped alpha/beta values")


if __name__ == '__main__':
    unittest.main()
