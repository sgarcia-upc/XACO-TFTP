#!/usr/bin/env python3
import sys
import argparse
sys.path.append("../lib/")
import tftp_lib
import tftp_pkg as pkg

from socket import *

def main(server="localhost", port=12000, size=512, mode="octet"):
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
                    file = command[1]
                    msg = pkg.generate_rrq(file, mode)
                    clientSocket.sendto(msg,(server,port))
                    print("{} {} {}".format("RRQ", file, mode))
                    tftp_lib.recv_file(clientSocket, server, port, file, size, mode)
                    clientSocket.close()

            elif command[0] == 'put':
                if len(command) != 2 and len(command) != 3:
                    invCommand = True

                else:
                    file = command[1]
                    msg = pkg.generate_wrq(file, mode)
                    clientSocket.sendto(msg,(server,port))
                    print("{} {} {}".format("WRQ", file, mode))
                    ack_num = -1
                    while ack_num != 0:
                        ack, add = clientSocket.recvfrom(4)
                        ack_num =  pkg.decodificate_ack(ack)
                        print("receiving ACK: %s"%(ack_num))
                        
                    tftp_lib.send_file(clientSocket, server, port, file, size, mode)
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
    parser.add_argument('-m','--mode', help='Modo de transmission de los ficheros', default="octet")
    
    parser.add_argument('--size', help='Tamaño paquete', default=512)
    args = parser.parse_args()
    
    if args.mode != "octet" and args.mode != "netascii":
        print("El mode ha de ser 'octet' o 'netascii' (siendo octet el modo por defecto)")
        sys.exit(1)
    
    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(server=args.server, port=int(args.port), size=int(args.size), mode=args.mode)
