import chess
import chess.engine

def init_stockfish():
    engine_path = 'cobra/src/stockfish'  # ARM64 Stockfish binary compiled from source
    return chess.engine.SimpleEngine.popen_uci(engine_path)