# Example UDP socket client that fires some text at a server

from socket import *

# Default to running on localhost, port 12000
serverName = 'localhost'
serverPort = 12000

# Request IPv4 and UDP communication
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Read in some text from the user
message = input('Escriba una frase en minusculas:')

# Send the text and then wait for a response 
clientSocket.sendto(message.encode(),(serverName,serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

# Print the converted text and then close the socket
print (modifiedMessage.decode())
clientSocket.close()
