import chess
import chess.engine
import sys
import os

def init_stockfish():
    if getattr(sys, 'frozen', False):
        # When the cobra process is created by Unity as a binary, use the path provided by sys._MEIPASS
        application_path = sys._MEIPASS
    else:
        # If running as a .py file, use default directory 
        application_path = os.path.dirname(os.path.abspath(__file__))

    # path name
    stockfish_binary = 'stockfish_nnue_ARM64'

    #full path to the Stockfish binary
    engine_path = os.path.join(application_path, stockfish_binary)

    # Ensure the binary is permissable as a executable, for macOS 
    os.chmod(engine_path, 0o755)

    return chess.engine.SimpleEngine.popen_uci(engine_path)
