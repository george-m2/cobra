import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)  # REP - reply/RequestSocket
socket.bind("tcp://*:5555")

while True:
    #  wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)
    # time delay - depends on length of tree search
    time.sleep(1)
    #  Send reply back to Chess.NET
    socket.send("test".encode('utf-8'))
