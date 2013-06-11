import socket
import sys

HOST, PORT = "10.0.0.86", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	sock.connect((HOST, PORT))
	while 1:
	    # Connect to server and send data
	    sock.sendall(data + "\n")

	    # Receive data from the server and shut down
	    received = sock.recv(1024)
	    print "Received: {}".format(received)
finally:
    sock.close()
