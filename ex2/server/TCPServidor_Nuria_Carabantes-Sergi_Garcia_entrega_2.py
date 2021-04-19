#!/usr/bin/env python3
import sys
import time
import argparse

from socket import *

def main(port=12000, size=512):

    # Setup IPv4 UDP socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    
    # Specify the welcoming port of the server
    serverSocket.bind(('', port))
    
    serverSocket.listen(1)
    print ("Esperando conexiones...")
    while True:
        
        connectionSocket, clientAddress = serverSocket.accept()
        message = connectionSocket.recv(size)
        msg = message.decode()

        print("Client connected {} -- ".format(clientAddress, msg), end='')
        command = msg.split()
        if len(command) > 0:
            if (command[0] == "get"):
                print("GET /{}".format(command[1])) 
                # Check if file exists 
                try:
                    f = open(command[1], "rb")
                    data = f.read(size)
                    print(" enviando... %s" %len(data))
                    while (len(data) > 0):
                        if (connectionSocket.send(data)):
                            if(len(data) == size):
                                data = f.read(size)
                                if (len(data) == 0): # Si es un fichero multiplo de size enviamos un paquete con 0 bytes de datos para comunicar al cliente que hemos acabado
                                    connectionSocket.send(data)
                            else:
                                data = bytes()
                        print(" enviando... %s" %len(data))
                            
                        
                except IOError as e:
                    print("File requested not found")
                    connectionSocket.send(bytes()) ## TEMPORAL, send 0 bytes to the client, this creates a new blank file
                    print(e)
                finally:
                    try:
                        f.close()
                    except e:
                        print(e)
    
            if (command[0] == "put"):
                if len(command) == 2:
                    print("PUT {}".format(command[1])) 
                    fichero_destino=command[1]
            
                if len(command) == 3:
                    print("PUT {} -> {}".format(command[1], command[2])) 
                    fichero_destino=command[2]
    
     
                data = connectionSocket.recv(size)
                print("recibiendo... %s" %len(data))
                try:
                    f = open(fichero_destino, "wb")
    
                    while (data):
                        f.write(data)
    
                        if (len(data) == size):
                            # Vamos a pedir mas datos en caso de que los haya
                            data = connectionSocket.recv(size)
                        else:
                            data = bytes()
                        print("recibiendo... %s" %len(data))
    
                except IOError:
                     print("File requested not found")
                except timeout:
                     print("timeout")
                finally:
                     try:
                        f.close()
                        #serverSocket.close()
                     except:
                        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port', help='Puerto destino', default=12000)
    parser.add_argument('--size', help='Tamaño paquete', default=512)
    args = parser.parse_args()
    
    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(port=int(args.port), size=int(args.size))
