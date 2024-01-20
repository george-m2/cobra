import zmq
import chess
import movegen
import argparse
import json
import platform
import os
import chess.engine
from engines import init_stockfish

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
        # If engine name is unknown or missing, return default settings
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

    # ZeroMQ socket setup
    context = zmq.Context() 
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555") #loopback

    if use_stockfish:
        stockfish_engine = init_stockfish()

    print(use_stockfish)

    while True:
        san = socket.recv().decode('utf-8') #receive move and normalise to utf-8
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

def get_depth_from_unity(file_path: str) -> int:
    """Reads the depth from the JSON specified by file_path. The depth int should be written to the file in the Chess.NET settings.

    Args:
        file_path (str): The path to the file containing the depth.

    Returns:
        int: The depth.
    """
    with open(file_path, 'w') as f:
        config = json.load(f)
        return config["depth"]

def standalone_cli_args():
    """Command line arguments for standalone use (not being called by the Chess.NET process) cobra engine.

    Returns:
        ArgumentParser object: The parser object containing the command line arguments.
    """
    parser = argparse.ArgumentParser(description='cobra engine with minimax/alpha-beta pruning algorithm')
    parser.add_argument('--depth', type=int, help='Depth of search')
    parser.add_argument('--use-stockfish', action='store_true', help='Use Stockfish(NNUE) engine')
    return parser.parse_args()
    