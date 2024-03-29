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
            get_ACPL(acpl_board_clone, move, acpl_array, stockfish_engine)  # get acpl value of the players move)
        board.push(move)
        start_time = time.time()
        if use_stockfish:
            result = stockfish_engine.play(board, chess.engine.Limit(depth=depth))  # create move, stockfish
            generated_move = result.move
        else:
            generated_move = movegen.next_move(depth, board)  # create move, cobra
        end_time = time.time()
        delta_time = round((end_time - start_time), 2)  # time taken to create the move, rounded to 2dp
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
    Returns:
        chess.Move: The move inputted by the user
    """
    example_move = list(board.legal_moves)[0]
    move = input(f"\nYour move (An example move could be {example_move}):\n")
    try:
        parsed_move = board.parse_san(move)
        if parsed_move in board.legal_moves:
            return parsed_move
        else:
            print("Invalid move, try again")
            return input_move(board)
    except ValueError:
        print("Invalid move, try again")
        return input_move(board)


def get_ACPL(board, move, acpl_array, stockfish_engine):
    """
    Standalone function to output the ACPL value of a move. Return value is the normalised ACPL, achieved by dividing by 100.
    Args:
        board: chess.Board
        move: chess.Move
        acpl_array: List of ACPL values to use in the ACPL graph
        stockfish_engine: Stockfish instance
    """
    acpl_white_board = board.copy()
    acpl_value = analyse.generate_ACPL(acpl_white_board, move, stockfish_engine)
    acpl_value = acpl_value / 100
    acpl_array.append(acpl_value)
    print(f"Accuracy of White's move: {acpl_value}", f"Next to move: {board.turn}")


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

    board_str = ""
    for square in chess.SQUARES_180: # 180 degree rotated board
        piece = board.piece_at(square)
        if piece:  # if there's a piece at the current square
            symbol = piece.symbol()
            board_str += icons.get(symbol, symbol) + " " # get the unicode icon for the piece
        else:
            board_str += icons["."] + " " # empty square
        if chess.square_file(square) == chess.square(7, 0):
            board_str += "\n"  # newline at the end of each row

    print(board_str)
    return board_str
