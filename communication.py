import zmq
import chess
import movegen
import argparse
import json
import platform
import os

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
        return f"{os.getenv('HOME')}/Library/Application Support/unity.DefaultCompany.Chess.NET/settings.json"
    
def read_settings_file_from_JSON(file_path: str) -> dict:
    """Reads the JSON file specified by file_path.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file.
    """
    if not os.path.exists(file_path): # If the file doesn't exist, return default depth
        return {"depth": 3}

    with open(file_path, 'r') as f:
        return json.load(f)
    

    
    

def communicate():
    board = chess.Board()
    depth = read_settings_file_from_JSON(get_unity_persistance_path())["depth"]

    # Setting up the ZeroMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP - reply/RequestSocket
    socket.bind("tcp://*:5555")

    while True:
        # Wait for the next request from the Unity
        san = socket.recv().decode('utf-8')
        print("Received PGN: %s" % san)

        # Process the PGN and push it to the board
        move = board.parse_san(san)
        board.push(move)
        print(board)

        # Generate a move
        generated_move = movegen.next_move(depth, board)
        board.push(generated_move)
        print(board)

        # Send the generated move and evaluation score back to Unity
        socket.send(f"{generated_move}".encode('utf-8'))

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

    