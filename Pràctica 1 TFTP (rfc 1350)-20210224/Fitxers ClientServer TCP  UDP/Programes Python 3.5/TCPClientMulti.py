# Example TCP socket client that connects to a server that upper cases text
import sys
from socket import *

# Read until we get \n on the socket, return the line of text without the \n
def getLine(sock):
    line = ""
    while True:
        ch = sock.recv(1)
        if (not ch) or (ch == "\n"):
            break
        line += ch
    return line
    
# Default to running on localhost, port 12000
serverName = 'localhost'
serverPort = 12000

# Optional server name argument
if (len(sys.argv) > 1):
	serverName = sys.argv[1]

# Optional server port number
if (len(sys.argv) > 2):
	serverPort = int(sys.argv[2])

# Request IPv4 and TCP communication
clientSocket = socket(AF_INET, SOCK_STREAM)

# Open the TCP connection to the server at the specified port 
clientSocket.connect((serverName,serverPort))

while True:
    # Read in some text from the user
    sentence = raw_input('Enter text: ')
    if len(sentence) == 0:
        break

    # Send the text and then wait for a response 
    clientSocket.send(sentence + "\n")
    
    # Receive a \n terminated line of text from the server
	# While code like 'modifiedSentence = clientSocket.recv(2048)'
	# would often work, there is no guarantee and a really long
	# string from the client might get returned by several calls to recv()
    modifiedSentence = getLine(clientSocket);
    
    print 'Response: ', modifiedSentence

clientSocket.close()
