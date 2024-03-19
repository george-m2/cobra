import time
import chess
import analyse
import chess.engine
import movegen


def standalone_use(board: chess.Board, depth: int, use_stockfish: bool, acpl_val: bool,
                   stockfish_engine: False):
    game_over = False
    acpl_array = []
    render_board_with_icons(board)
    while not game_over:
        move = input_move(board)
        if acpl_val:
            acpl_board_clone = board.copy()
            get_acpl(acpl_board_clone, move, acpl_array, stockfish_engine)  # get acpl value of the players move)
        board.push(move)
        start_time = time.time()
        if use_stockfish:
            result = stockfish_engine.play(board, chess.engine.Limit(depth=depth))  # create move, stockfish
            generated_move = result.move
        else:
            generated_move = movegen.next_move(depth, board)  # create move, cobra
        end_time = time.time()
        delta_time = round((end_time - start_time), 2)  # time to make time, rounded to 2dp
        print(f"Move execution time: {delta_time} seconds")
        san = board.san(generated_move)
        board.push_san(san)
        render_board_with_icons(board)

        if board.is_game_over():
            game_over = True
            result = board.result()
            print(f"Game over! Result: {result}")


def input_move(board) -> chess.Move:
    """
    Function to handle input from the command line interface.
    Args:
        board: chess.Board object
    """
    move = input(f"\nYour move (An example move could be {list(board.legal_moves)[0]}):\n")
    for legal_move in board.legal_moves:
        if str(legal_move) == move:
            return board.parse_san(move)
        else:
            print("Invalid move, try again")
            return input_move(board)


def get_acpl(board, move, acpl_array, stockfish_engine):
    acpl_white_board = board.copy()
    acpl_value = analyse.generate_ACPL(acpl_white_board, move, stockfish_engine)
    acpl_array.append(acpl_value)
    print(f"Accuracy of White's move: {acpl_value}", f"Next to move: {board.turn}")
    return acpl_array


def render_board_with_icons(board: chess.Board) -> str:
    """
    Function to render the chess board with unicode icons.
    Args:
        board: chess.Board object
    Returns:
        str: The rendered chess board
    """
    icons = {
        "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
        "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
        ".": "·"
    }

    # Create an empty board representation with dots
    board_str = ""
    for square in chess.SQUARES_180:
        piece = board.piece_at(square)
        if piece:  # If there's a piece at the current square
            symbol = piece.symbol()
            board_str += icons.get(symbol, symbol) + " "
        else:
            board_str += icons["."] + " "
        if chess.square_file(square) == chess.square(7, 0):
            board_str += "\n"  # Add a newline at the end of each row

    print(board_str)
    return board_str
