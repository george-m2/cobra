import zmq
import chess
import movegen
import argparse
import platform
import os
import chess.engine
import sys
import chess.pgn
import json
from engines import init_stockfish
import analyse
import time


def signal_handler(sig, frame):
    """Handles the SIGINT signal, which is sent on exit.

    Args:
        sig (int): The signal number.
        frame (frame): The current stack frame.
    """
    print("SIGINT received, exiting...")
    sys.exit(0)


def get_unity_persistance_path() -> str:
    """Gets the path to the Unity persistence file. Chess.NET's JSON settings file is stored at this path, which is platform dependent.

    Returns:
        str: The path to the Unity persistence file.
    """
    if platform.system() == "Windows":
        return f"{os.getenv('APPDATA')}/../LocalLow/DefaultCompany/Chess.NET/settings.json"
    elif platform.system() == "Linux":
        return f"{os.getenv('HOME')}/.config/unity3d/DefaultCompany/Chess.NET/settings.json"
    elif platform.system() == "Darwin":  # macOS
        return f"{os.getenv('HOME')}/Library/Application Support/DefaultCompany/Chess_NET/settings.json"


def read_settings_file_from_JSON(file_path: str) -> dict:
    """Reads the Unity settings file from JSON file specified by file_path.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file.
    """
    default_settings = {"depth": 3, "use_stockfish": False, "stockfishSkillLevel": 2, "ACPL": False}

    if not os.path.exists(file_path):  # If the file doesn't exist, return default settings
        return default_settings

    with open(file_path, 'r') as f:
        settings = json.load(f)

    # Normalize the engine name to handle whitespace inconsistencies
    engine = settings.get("selectedEngine", "").strip()
    depth = settings.get("depth")
    skill_level = settings.get("stockfishSkillLevel")
    acpl_val = settings.get("ACPL")

    # What engine has the user selected?
    if engine == "Stockfish":
        return {"depth": depth, "use_stockfish": True, "skill_level": skill_level, "ACPL": acpl_val}
    elif engine == "cobra":
        return {"depth": depth, "use_stockfish": False,
                "acpl_val": acpl_val}  # no need to include skill level for cobra
    else:
        # If engine name is unknown or missing, return cobra engine, depth 3 
        return default_settings


def communicate():
    """
    Function to handle communication between cobra/Chess.NET.

    This function reads settings from a JSON file or passed as CLI args, initialises the chess board,
    and listens for incoming PGN moves over a ZeroMQ socket.
    It then generates a response move based on the received move and sends it back.

    """
    parser = standalone_cli_args()
    args = parser.parse_args()
    settings = read_settings_file_from_JSON(get_unity_persistance_path())

    # determine settings based on args or fall back to settings.json
    depth = args.depth if args.depth is not None else settings.get("depth", 3)
    use_stockfish = args.use_stockfish if args.use_stockfish is not None else settings.get("use_stockfish", False)
    skill_level = args.skill_level if args.skill_level is not None else settings.get("skill_level", 2)
    acpl_val = args.acpl if args.acpl is not None else settings.get("ACPL", False)

    board = chess.Board()

    # ZeroMQ socket setup
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")  # loopback

    if use_stockfish:
        stockfish_engine = init_stockfish()
        stockfish_engine.configure({"Skill Level": skill_level})
        print(f"Depth: {depth}, Stockfish: {use_stockfish}, Skill: {skill_level}", f"ACPL: {acpl_val}")
    else:
        print(f"Depth: {depth}, cobra: True", f"ACPL: {acpl_val}")

    while True:
        san = socket.recv().decode('utf-8')  # receive move and normalize to utf-8
        if san == "SHUTDOWN":
            print("Received SHUTDOWN, exiting...")
            socket.close()
            context.term()
            if use_stockfish:
                stockfish_engine.quit()
            sys.exit(0)
        if san == "GAME_END":
            if use_stockfish:
                stockfish_engine.close()  # engine is closed and reopened to avoid memory leak

            print("Received GAME_END command")
            game = chess.pgn.Game.from_board(board)
            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)  # PGN exporter
            pgn_string = game.accept(exporter)
            best_move_count = analyse.analyse_best_move(pgn_string)
            blunder_count = analyse.analyse_blunders(pgn_string)

            # both values cannot be sent independently due to REP deadlock, therefore they are sent as a JSON object
            # https://zguide.zeromq.org/docs/chapter4/

            end_state_data = {"bestMoveCount": best_move_count, "blunderCount": blunder_count}

            end_state_data_json = json.dumps(end_state_data)
            socket.send(end_state_data_json.encode('utf-8'))
            socket.close()
            context.term()
            sys.exit(0)

        print("Received PGN: %s" % san)

        move = board.parse_san(san)
        board.push(move)
        print(board)

        start_time = time.time()
        if use_stockfish:
            result = stockfish_engine.play(board, chess.engine.Limit(depth=depth))  # uses depth from JSON
            generated_move = result.move
        else:
            generated_move = movegen.next_move(depth, board)  # create move

        end_time = time.time()
        delta_time = end_time - start_time
        print(f"Move execution time: {delta_time} seconds")

        san = board.san(generated_move)
        if use_stockfish == False and acpl_val == True:
            stockfish_engine = init_stockfish()

        if acpl_val == True:
            acpl_value = analyse.generate_ACPL(board, generated_move, stockfish_engine)
        board.push_san(san)
        print(san, f"Accuracy: {acpl_value}", f"Next to move: {board.turn}")
        print(board)
        if acpl_val == True:
            response_data = {"move": san, "acpl": acpl_value}  # send move and ACPL value as JSON object
        else:
            response_data = {"move": san}
        response_json = json.dumps(response_data)
        socket.send(response_json.encode('utf-8'))


def standalone_cli_args():
    """Command line arguments for standalone use (not being called by the Chess.NET process) cobra engine.

    Returns:
        ArgumentParser object: The parser object containing the command line arguments.
    """
    parser = argparse.ArgumentParser(description='Cobra chess engine with minimax(AB) pruning algorithm. '
                                                 'George Maycock, 2024')
    parser.add_argument('--depth', type=int, default=None, help='Iterative depth for the engine.')
    parser.add_argument('--use-stockfish', nargs='?', const=True, default=None,
                        help='Use Stockfish engine instead of Cobra.')
    parser.add_argument('--acpl', nargs='?', const=True, default=None, help='Enable ACPL calculation.')
    parser.add_argument('--skill-level', type=int, default=None, help='Skill level for Stockfish engine.')
    args, unknown = parser.parse_known_args()
    if '--help' in unknown:
        parser.print_help()
        sys.exit(0)
    return parser
