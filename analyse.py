import chess
import chess.engine
import chess.pgn
import io 
from engines import init_stockfish

#TODO: make asynchronous
def analyse(pgn_source, is_pgn_file = False):
    """Analyse a PGN file or string with Stockfish and compares White's moves between the PGN and Stockfish's best move.\n
    Used for the best move counter in Chess.NET.

    Args:
        pgn_string (str): PGN string to analyse.
        pgn_file (bool, optional): Used for analysing a PGN file from disk. Defaults to False.

    Returns:
        int: Number of times Stockfish agreed with White's move.
    """    
    engine = init_stockfish()
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
            stockfish_move = engine.play(board, chess.engine.Limit(time=0.1)).move
            print(stockfish_move.uci())

            # Compare moves
            if move == stockfish_move:
                stockfish_agree_count += 1

        board.push(move)

    engine.quit()
    print("Number of times Stockfish agreed with White's move:", stockfish_agree_count)
    return stockfish_agree_count
