import zmq
import chess

board = chess.Board()


def process_pgn(pgn):
    move = board.parse_san(pgn)
    board.push(move)
    print(board)
    return pgn


# Setting up the ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REP)  # REP - reply/RequestSocket
socket.bind("tcp://*:5555")

while True:
    # Wait for the next request from the C# client
    san = socket.recv().decode('utf-8')
    print("Received PGN: %s" % san)

    # Process the PGN and return to Unity (placeholder)
    sending_move = process_pgn(san)

    # Send the best move back to the C# client
    socket.send(sending_move.encode('utf-8'))
