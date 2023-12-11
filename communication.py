import zmq

def process_pgn(pgn):
    # Placeholder for PGN processing and best move finding logic
    # minimax()
    return "e2e4"


# Setting up the ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REP)  # REP - reply/RequestSocket
socket.bind("tcp://*:5555")

while True:
    # Wait for the next request from the C# client
    pgn_message = socket.recv().decode('utf-8')
    print("Received PGN: %s" % pgn_message)

    # Process the PGN and find the best move
    best_move = process_pgn(pgn_message)

    # Send the best move back to the C# client
    socket.send(best_move.encode('utf-8'))
