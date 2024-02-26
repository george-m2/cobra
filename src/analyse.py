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

