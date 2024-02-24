import chess
import time
from eval import evaluate_board, move_value, check_end_game

MATE_SCORE = 9999  # arbitrary score for checkmate - checkmate condition is the best quantifiable outcome
MATE_THRESHOLD = 9990  # threshold for checkmate - if the score is above this, the game is over


def next_move(depth: int, board: chess.Board) -> chess.Move:
    """
    Determine the next best move.

    Args:
        depth (int): The depth to which the minimax algorithm should run.
        board (chess.Board): The current state of the chess board.
        debug (bool, optional): Whether to print debug information. Defaults to True.

    Returns:
        chess.Move: The best move determined by the algorithm.
    """
    t0 = time.time()
    move = find_best_move_minimax(depth, board)  # minimax call
    elapsed_time = time.time() - t0

    print(f"Depth: {depth}, Time: {elapsed_time:.2f}")
    return move


def get_move_quality(move, board, end_game):
    """
    Calculate the quality of a move based on the board and end game status.

    Args:
        move (chess.Move): The move to evaluate.
        board (chess.Board): The current state of the chess board.
        end_game (bool): Whether the game is in an end game state.

    Returns:
        float: The quality of the move.
    """
    return move_value(board, move, end_game)


def get_ordered_moves(board: chess.Board) -> list[chess.Move]:
    """
    Get legal moves sorted by estimated quality.

    Args:
        board (chess.Board): The current state of the chess board.

    Returns:
        list[chess.Move]: A list of legal moves sorted by their estimated quality.
    """
    end_game = check_end_game(board)
    sorted_moves = sorted(board.legal_moves, key=lambda move: get_move_quality(move, board, end_game),
                          reverse=board.turn == chess.WHITE)
    return sorted_moves


def find_best_move_minimax(depth: int, board: chess.Board) -> chess.Move:
    """
    Determine the highest value move using the evaluation function.

    Args:
        depth (int): The depth to which the minimax algorithm should run.
        board (chess.Board): The current state of the chess board.

    Returns:
        chess.Move: The best move determined by the algorithm.
    """
    maximize = board.turn == chess.WHITE
    best_move = float("-inf") if maximize else float("inf")
    best_move_found = None

    moves = get_ordered_moves(board)
    for move in moves:
        board.push(move)
        if board.can_claim_draw():
            value = 0.0
        else:
            value = minimax(depth - 1, board, -float("inf"), float("inf"), not maximize)
        board.pop()
        if (maximize and value > best_move) or (not maximize and value < best_move):
            best_move = value
            best_move_found = move

    return best_move_found


def minimax(depth: int, board: chess.Board, alpha: float, beta: float, is_maximising_player: bool) -> float:
    """
    Minimax algorithm with alpha-beta pruning.
    Minimax pseudocode from https://en.wikipedia.org/wiki/Minimax 
    AB pruning pseudocode from https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning

    Args:
        depth (int): The maximum depth of the game tree that the algorithm should explore.
        board (chess.Board): The current state of the chess board.
        alpha (float): The best (highest) score that the maximizing player has found so far.
        beta (float): The best (lowest) score that the minimizing player has found so far.
        is_maximising_player (bool): True if the current player is the maximizing player, False if they are the minimizing player.

    Returns:
        float: The score of the best move that the current player can make. A high score is good for the maximizing player and bad for the minimizing player.
    """

    if board.is_checkmate():
        return -MATE_SCORE if is_maximising_player else MATE_SCORE
    elif board.is_game_over():
        return 0

    if depth == 0:
        return evaluate_board(board)

    if is_maximising_player:
        best_move = float("-inf")
        for move in get_ordered_moves(board):
            board.push(move)
            curr_move = minimax(depth - 1, board, alpha, beta, False)
            board.pop()
            best_move = max(best_move, curr_move)
            alpha = max(alpha, best_move)
            if beta <= alpha:
                break
        return best_move
    else:
        best_move = float("inf")
        for move in get_ordered_moves(board):
            board.push(move)
            curr_move = minimax(depth - 1, board, alpha, beta, True)
            board.pop()
            best_move = min(best_move, curr_move)
            beta = min(beta, best_move)
            if beta <= alpha:
                break
        return best_move
