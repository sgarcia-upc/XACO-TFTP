#!/usr/bin/env python3
import sys
import argparse

from socket import *

def main(server="localhost", port=12000):
    sortir = False
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    while sortir == False:
        invCommand = False
        # Read in some text from the user
        msg = input('> ')
        command = msg.split()
        if len(command) > 0:
            if command[0] == 'get':
                if len(command) != 2:
                    invCommand = True

                if not invCommand:
                    # Send file name
                    clientSocket.sendto(msg.encode(),(server,port))

                    # TODO: receive ok msg 
                    # receive file

                    data, serverAddress = clientSocket.recvfrom(512)
                    try:
                        f = open(command[1], "wb")
                        
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
                    
                    

            elif command[0] == 'put':
                if len(command) != 2 or len(command) != 3:
                    invCommand = True 
                
                else:
                    #enviamos el comando con el fichero que vamos a subir
                    clientSocket.sendto(msg.encode(),(server,port))
                    try:
                        # TODO: if file not exists, what happends with the client
                        f = open(fichero_origen, "rb")
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

            elif command[0] == 'exit':
                sortir = True 
            else:
                invCommand = True
        else: 
            invCommand = True

        if invCommand:
            print("Invalid command")
    
    clientSocket.close()
    print("bye!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--server', help='IP/DNS destino', default="localhost")
    parser.add_argument('-p','--port', help='Puerto destino', default=12000)
    args = parser.parse_args()
    
    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(server=args.server, port=int(args.port))
