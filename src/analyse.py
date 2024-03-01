import chess
import chess.engine
import chess.pgn
import io
from engines import init_stockfish
from movegen import get_ordered_moves

engine = init_stockfish()


# TODO: make asynchronous
def analyse_best_move(pgn_source, is_pgn_file=False):
    """Analyse a PGN file or string with Stockfish and compares White's moves between the PGN and Stockfish's best move.\n
    Used for the best move counter in Chess.NET.

    Args:
        pgn_source (str): PGN string to analyse.
        is_pgn_file (bool, optional): Used for analysing a PGN file from disk. Defaults to False.

    Returns:
        int: Number of times Stockfish agreed with White's move.
    """
    if is_pgn_file:
        with open(pgn_source, 'r') as pgn:
            game = chess.pgn.read_game(pgn)
    else:
        pgn_string = io.StringIO(pgn_source)
        game = chess.pgn.read_game(pgn_string)

    board = game.board()
    stockfish_agree_count = 0

    for move in game.mainline_moves():
        if board.turn == chess.WHITE:
            # Get Stockfish's best move for the current position
            stockfish_move = engine.play(board, chess.engine.Limit(time=0.5)).move
            print(stockfish_move.uci())

            # Compare moves
            if move == stockfish_move:
                stockfish_agree_count += 1

        board.push(move)

    print("Number of times Stockfish agreed with White's move:", stockfish_agree_count)
    return stockfish_agree_count


def analyse_blunders(pgn_source, is_pgn_file=False):
    """
    Analyse a PGN file or string with Stockfish and compares White's moves between the PGN. \n
    A blunder is determined as the bottom 50% of all possible moves in terms of centipawn analysis.\n
    Args:
        pgn_source (str): PGN string to analyse.
        is_pgn_file (bool, optional): Used for analysing a PGN file from disk. Defaults to False.
    Returns:
        int: Number of blunders in the PGN.
    """
    if is_pgn_file:
        with open(pgn_source, 'r') as pgn:
            game = chess.pgn.read_game(pgn)
    else:
        pgn_string = io.StringIO(pgn_source)
        game = chess.pgn.read_game(pgn_string)

    board = game.board()
    blunder_count = 0
    move_list = []
    blunder_count = 0

    for move in game.mainline_moves():
        move_list = get_ordered_moves(board) # get ordered moves, ordered by quality dsc
        num_blunders = int(len(move_list) * 0.25)  # bottom 25% of moves are considered blunders
        blunder_moves = move_list[-num_blunders:]
        if move in blunder_moves:
            blunder_count += 1
        board.push(move)

    print("Number of blunders:", blunder_count)
    return blunder_count

def generate_ACPL(board, move, engine=None):
    """
    Evaluate the given move by comparing it against the engine's best move.
    The ACPL is positive if it's a loss for White, and negative if it's a loss for Black,
    indicating the move's quality from the player's perspective.

    Args:
        engine (chess.engine.SimpleEngine): The chess engine for evaluation.
        board (chess.Board): The current board state before the move.
        move (chess.Move): The move to evaluate.

    Returns:
        int: The centipawn loss of the move, compared to the engine's best move,
             positive for White's loss and negative for Black's loss.
    """

    # evaluate before the move
    info_before = engine.analyse(board, chess.engine.Limit(depth=15))
    score_before = info_before["score"].pov(board.turn).score(mate_score=10000)

    # evaluate after the move
    board.push(move)
    info_after = engine.analyse(board, chess.engine.Limit(depth=15))
    score_after = info_after["score"].pov(board.turn).score(mate_score=10000)

    if board.turn == chess.WHITE:
        # It was Black's turn, so make the ACPL negative to reflect Black's perspective
        cp_loss = score_before - score_after
    else:
        # It was White's turn, so make the ACPL positive to reflect White's perspective
        cp_loss = score_after - score_before

    return cp_loss

