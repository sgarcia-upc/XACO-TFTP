#https://katie.mtech.edu/classes/archive/f12/csci466/assign/fi#leserver/
# TCP server program that upper cases text sent from the client
from socket import *
import sys
import threading
import thread

# Read until we get \n on the socket, return the line of text without the \n
def getLine(sock):
    line = ""
    while True:
        ch = sock.recv(1)
        if (not ch) or (ch == "\n"):
            break
        line += ch
    return line
    
# Worker thread, receives a \n terminated line then sends client 
# capitalized version.  Keep doing this until client send an blank line.
def worker(sock,addr):
    print '\nWorker started: ', addr
    while 1:
        sentence = getLine(sock)
        if not sentence:
            break
        print 'Worker got sentence: ', sentence
        capitalizedSentence = sentence.upper()
        capitalizedSentence += "\n";
        
        # Send back the converted text to the client	    
        sock.send(capitalizedSentence)
    sock.close()
    print 'Worker finished: ', addr

# Default port number server will listen on
serverPort = 12000

# Optional server port number
if (len(sys.argv) > 1):
	serverPort = int(sys.argv[1])

# Request IPv4 and TCP communication
serverSocket = socket(AF_INET,SOCK_STREAM)

# The welcoming port that clients first use to connect
serverSocket.bind(('',serverPort))

# Start listening on the welcoming port
serverSocket.listen(1)
print 'The server is ready to receive on port = ', serverPort
while 1:
	# Wait for a client to connect to welcome port, establish
    # a new socket connection to the client on a transient port
    print 'Waiting for client connection...'
    
    clientSocket, addr = serverSocket.accept()
    print 'Client arrived: ', addr
    thread.start_new_thread(worker, (clientSocket, addr))
