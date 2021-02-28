# Example TCP socket client that connects to a server that upper cases text
import sys
from socket import *

# Default to running on localhost, port 12000
serverName = 'localhost'
serverPort = 12000

# Request IPv4 and TCP communication
clientSocket = socket(AF_INET, SOCK_STREAM)

# Open the TCP connection to the server at the specified port 
clientSocket.connect((serverName,serverPort))

# Read in some text from the user
sentence = input('Escriba una frase en minusculas:')

# Send the text and then wait for a response 
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)

# Print the converted text and then close the socket
print ('From Server:', modifiedSentence.decode())
clientSocket.close()
