import zmq
import chess
import movegen
import argparse
import json
import platform
import os
import chess.engine
import sys
import chess.pgn
from engines import init_stockfish
from analyse import analyse

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
    elif platform.system() == "Darwin": # macOS
        return f"{os.getenv('HOME')}/Library/Application Support/DefaultCompany/Chess_NET/settings.json"
    
def read_settings_file_from_JSON(file_path: str) -> dict:
    """Reads the Unity settings file from JSON file specified by file_path.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file.
    """
    default_settings = {"depth": 3, "use_stockfish": False}
    
    if not os.path.exists(file_path):  # If the file doesn't exist, return default settings
        return default_settings

    with open(file_path, 'r') as f:
        settings = json.load(f)

    # Normalize the engine name to handle whitespace inconsistences 
    engine = settings.get("selectedEngine", "").strip()

    depth = settings.get("depth", 3)
    
    # What engine has the user selected?
    if engine == "Stockfish":
        return {"depth": depth, "use_stockfish": True}
    elif engine == "cobra":
        return {"depth": depth, "use_stockfish": False}
    else:
        # If engine name is unknown or missing, return cobra engine, depth 3 
        return default_settings

    
def communicate():
    """
    Function to handle communication between cobra/Chess.NET.

    This function reads settings from a JSON file, initializes the chess board,
    and listens for incoming PGN moves over a ZeroMQ socket.
    It then generates a response move based on the received move and sends it back.

    Returns:
        None
    """
    board = chess.Board()
    settings = read_settings_file_from_JSON(get_unity_persistance_path()) #reads settings from Chess.NET in JSON file
    depth = settings["depth"]
    use_stockfish = settings["use_stockfish"]
    elo = settings["elo"]

    # ZeroMQ socket setup
    context = zmq.Context() 
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555") #loopback

    if use_stockfish:
        stockfish_engine = init_stockfish()

    print(use_stockfish)
    stockfish_engine.configure({"UCI_Elo": elo}) #set elo for Stockfish
    
    while True:
        san = socket.recv().decode('utf-8') #receive move and normalise to utf-8
        if san == "SHUTDOWN":
            print("Received SHUTDOWN, exiting...")
            socket.close()
            context.term()
            sys.exit(0)
        if san == "GAME_END":
            stockfish_engine.close() #engine is closed and reopened to avoid memory leak

            print("Received GAME_END command")
            game = chess.pgn.Game.from_board(board)
            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
            pgn_string = game.accept(exporter)
            best_move_count = analyse(pgn_string)

            socket.send(f"{best_move_count}".encode('utf-8'))
            socket.close()
            context.term()
            sys.exit(0)
           
        print("Received PGN: %s" % san)

        move = board.parse_san(san)
        board.push(move)
        print(board)

        if use_stockfish:
            result = stockfish_engine.play(board, chess.engine.Limit(depth=depth)) #uses depth from JSON 
            generated_move = result.move
        else:
            generated_move = movegen.next_move(depth, board) #create move

        san = board.san(generated_move)
        board.push_san(san)
        print(board)

        socket.send(f"{san}".encode('utf-8'))
    
def standalone_cli_args():
    """Command line arguments for standalone use (not being called by the Chess.NET process) cobra engine.

    Returns:
        ArgumentParser object: The parser object containing the command line arguments.
    """
    parser = argparse.ArgumentParser(description='cobra engine with minimax/alpha-beta pruning algorithm')
    parser.add_argument('--depth', type=int, help='Depth of search')
    parser.add_argument('--use-stockfish', action='store_true', help='Use Stockfish(NNUE) engine')
    return parser.parse_args()
    