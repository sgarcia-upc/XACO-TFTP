#!/usr/bin/env python3
import sys
import argparse
import tftp_lib

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
                print(" put <file> [name]\t Upload specified file to the server. The optional name parameter can be used to upload the file with another name")
                print(" exit\t\t\t Exit from this program")
                print(" ?\t\t\t Show this help")
            elif command[0] == 'get':
                if len(command) != 2:
                    invCommand = True

                if not invCommand:
                    # Send file name
                    clientSocket.sendto(msg.encode(),(server,port))
                    tftp_lib.recv_file(clientSocket, command[1], size) 
                    clientSocket.close()

            elif command[0] == 'put':
                if len(command) != 2 and len(command) != 3:
                    invCommand = True 
                
                else:
                    clientSocket.sendto(msg.encode(),(server,port))
                    tftp_lib.send_file(clientSocket, server, port, command[1], size)
                    clientSocket.close()

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
    parser.add_argument('--size', help='Tamaño paquete', default=512)
    args = parser.parse_args()
    
    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(server=args.server, port=int(args.port), size=int(args.size))
