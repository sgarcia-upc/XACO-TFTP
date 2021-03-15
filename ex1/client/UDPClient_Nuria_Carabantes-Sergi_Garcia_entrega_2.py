#!/usr/bin/env python3
import sys
import argparse

from socket import *

def main(server="localhost", port=12000, size=512):
    sortir = False
    while sortir == False:
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        invCommand = False
        # Read in some text from the user
        msg = input('> ')
        command = msg.split()
        if len(command) > 0:
            if command[0] == '?':
                print(" get <file>\t\t Download specified file from the server")
                print(" post <file> [name]\t Upload specified file to the server. The optional name parameter can be used to upload the file with another name")
                print(" exit\t\t\t Exit from this program")
                print(" ?\t\t\t Show this help")
            elif command[0] == 'get':
                if len(command) != 2:
                    invCommand = True

                if not invCommand:
                    # Send file name
                    clientSocket.sendto(msg.encode(),(server,port))

                    # TODO: receive ok msg 
                    # receive file

                    data, serverAddress = clientSocket.recvfrom(size)
                    try:
                        f = open(command[1], "wb")
                        
                        while (data):
                            f.write(data)
                            
                            if (len(data) == size):
                                # Vamos a pedir mas datos en caso de que los haya
                                data, serverAddress = clientSocket.recvfrom(size)
                            else:
                                data = bytes()
                            
                    except IOError:
                        print("File requested not found")
                    except timeout:
                        print("timeout")
                    finally:
                        try:
                            f.close()
                            clientSocket.close()
                        except:
                            pass
                    
                    

            elif command[0] == 'put':
                if len(command) != 2 and len(command) != 3:
                    invCommand = True 
                
                else:
                    #enviamos el comando con el fichero que vamos a subir
                    clientSocket.sendto(msg.encode(),(server,port))
                    try:
                        # TODO: if file not exists, what happends with the client
                        f = open(command[1], "rb")
                        data = f.read(size)
                        while (len(data) > 0):
                            if (clientSocket.sendto(data, (server, port))):
                                if(len(data) == size):
                                    data = f.read(size)
                                    if (len(data) == 0): # Si es un fichero multiplo de size enviamos un paquete con 0 bytes de datos para comunicar al cliente que hemos acabado
                                        clientSocket.sendto(data, (server, port))
                                else:
                                    data = bytes()
                    
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
    
    print("Goodbye !!!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--server', help='IP/DNS destino', default="localhost")
    parser.add_argument('-p','--port', help='Puerto destino', default=12000)
    args = parser.parse_args()
    
    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(server=args.server, port=int(args.port))
