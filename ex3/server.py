#!/usr/bin/env python3
import sys
import time
import argparse
import tftp_lib

from socket import *

def main(port=12000, size=512):

    # Setup IPv4 UDP socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    
    # Specify the welcoming port of the server
    serverSocket.bind(('', port))
    
    print ("Esperando conexiones...")
    while True:
        message, clientAddress = serverSocket.recvfrom(size)
        msg = message.decode()

        print("Client connected {} -- ".format(clientAddress, msg), end='')
        command = msg.split()
        if len(command) > 0:
            if (command[0] == "get"):
                print("GET /{}".format(command[1])) 
                print(clientAddress)
                tftp_lib.send_file(serverSocket, clientAddress[0], clientAddress[1], command[1], size, "octet")
    
            if (command[0] == "put"):
                if len(command) == 2:
                    print("PUT {}".format(command[1])) 
                    fichero_destino=command[1]
            
                if len(command) == 3:
                    print("PUT {} -> {}".format(command[1], command[2])) 
                    fichero_destino=command[2]
  
                tftp_lib.recv_file(serverSocket, fichero_destino, size, "octet") 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port', help='Puerto destino', default=12000)
    parser.add_argument('--size', help='Tamaño paquete', default=512)
    args = parser.parse_args()
    
    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(port=int(args.port), size=int(args.size))
