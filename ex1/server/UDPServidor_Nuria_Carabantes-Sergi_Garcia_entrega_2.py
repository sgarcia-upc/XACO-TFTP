#!/usr/bin/env python3
import sys
import time
import argparse

from socket import *

def main(port=12000):

    # Setup IPv4 UDP socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    
    # Specify the welcoming port of the server
    serverSocket.bind(('', port))
    
    print ("Esperando conexiones...")
    while True:
        message, clientAddress = serverSocket.recvfrom(512)
        msg = message.decode()

        print("Client connected {} -- {}".format(clientAddress, msg))
        command = msg.split()
        if (command[0] == "get"):
            print("GET /{}".format(command[1])) 
            # Check if file exists 
            try:
                # TODO: if file not exists, what happends with the client
                f = open(command[1], "rb")
                data = f.read(512)
                while (len(data) > 0):
                    if (serverSocket.sendto(data, clientAddress)):
                        data = f.read(512)
                        if (len(data) == 0): # Si es un fichero multiplo de 512 enviamos un paquete con 0 bytes de datos para comunicar al cliente que hemos acabado
                            serverSocket.sendto(data, clientAddress)
                    
            except IOError as e:
                print("File requested not found")
                print(e)
            finally:
                try:
                    f.close()
                except:
                    pass

        if (command[0] == "put"):
            if len(command) == 2:
                print("PUT {}".format(command[1])) 
                fichero_destino=command[1]
        
            if len(command) == 3:
                print("PUT {} -> {}".format(command[1], command[2])) 
                fichero_destino=command[2]

 
		   data, serverAddress = clientSocket.recvfrom(512)
		   try:
				f = open(fichero_destino, "wb")

				while (data):
					 f.write(data)

					 if (len(data) == 512):
						  # Vamos a pedir mas datos en caso de que los haya
						  data, serverAddress = clientSocket.recvfrom(512)
					 else:
						  data = bytes()

		   except IOError:
				print("File requested not found")
		   except timeout:
				print("timeout")
		   finally:
				try:
					 f.close()
					 serverSocket.close()
				except:
					 pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port', help='Puerto destino', default=12000)
    args = parser.parse_args()
    
    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(port=int(args.port))
