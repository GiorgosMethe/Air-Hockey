import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 5402          # Reserve a port for your service.

s.connect((host, port))
while 1:
	data = s.recv(1024)
	print data
	if not data:
		print "server down"
		break
s.close                     # Close the socket when done