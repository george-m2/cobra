from communication import communicate
import sys
import signal
from communication import signal_handler

# Register the signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    communicate()
except Exception as e:
    print("Error: " + str(e))
    exit()
