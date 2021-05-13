#!/usr/bin/env python3
import sys
import os.path
import argparse
sys.path.append("../lib/")
import tftp_lib
import tftp_pkg as pkg

from socket import *

def main(server="localhost", port=12000, default_size=512, mode="octet"):
    size = default_size
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
                print(" mode \t\t\t Show actual file transfer mode")
                print(" octet \t\t\t Change mode to octet")
                print(" netascii \t\t Change mode to netascii")
                print(" size [size]\t\t Change pkg size")
                print(" exit\t\t\t Exit from this program")
                print(" ?\t\t\t Show this help")
            elif command[0] == 'size':
                if (len(command) > 1):
                    size = int(command[1])
                    print("Changed pkg size to: {}".format(size))
                else:
                    print("Current pkg size is: {}".format(size))
            elif command[0] == 'octet':
                mode = "octet"
                print("Mode changed to: '{}'".format(mode))
            elif command[0] == 'netascii':
                mode = "netascii"
                print("Mode changed to: '{}'".format(mode))
            elif command[0] == 'mode':
                print("Current mode is: '{}'".format(mode))
            elif command[0] == 'get':
                if len(command) != 2:
                    invCommand = True

                if not invCommand:
                    # Send file name
                    file = command[1]
                    msg = pkg.generate_rrq(file, mode)
                    msg = pkg.add_option_rrq_wrq(msg, "blksize", str(size))
                    clientSocket.sendto(msg,(server,port))
                    print("{} {} {}".format("RRQ", file, mode))
                    try:
                        tftp_lib.recv_file(clientSocket, server, port, file, size, mode)
                    except tftp_lib.FileNotFound as e:
                        print(e)

            elif command[0] == 'put':
                if len(command) != 2 and len(command) != 3:
                    invCommand = True

                else:
                    file = command[1]
                    if not os.path.isfile(file):
                        print("File: '{}' not found".format(file))
                        continue # Ask option again
                    filename = file
                    
                    if len(command) > 2:
                        filename = command[2] 

                    msg = pkg.generate_wrq(filename, mode)

                    if size != default_size: 
                        # Aka size no es 512
                        msg = pkg.add_option_rrq_wrq(msg, "blksize", str(size))

                    clientSocket.sendto(msg,(server,port))
                    print("{} {} {}".format("WRQ", filename, mode))
                    ack_num = -1
                    response, add = clientSocket.recvfrom(512)
                    op_code = pkg.decodificate_opcode(response)
                    decided_size = size
                    if op_code == "OACK":
                        print("receiving OACK")
                        blksize_detected = False
                        option_list = pkg.decodificate_oack(response)
                        for i in range(0, len(option_list), 2):
                            if option_list[i] == "blksize":
                                print ("Server accepted: {} with value {}".format(option_list[i], option_list[i+1]))
                                blksize_detected = True
                        if blksize_detected == False:
                            decided_size = defalut_size
                            print("Server doesn't accept blksize option")
                        
                    if op_code == "ACK":
                        if size != default_size: 
                            print("Server doesn't accept blksize option")
                        decided_size = size
                        ack_num =  pkg.decodificate_ack(response)
                        print("receiving ACK: %s"%(ack_num))
                        while ack_num != 0:
                            ack, add = clientSocket.recvfrom(4)
                            ack_num =  pkg.decodificate_ack(ack)
                            print("receiving ACK: %s"%(ack_num))
                        
                    tftp_lib.send_file(clientSocket, server, port, file, decided_size, mode)

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

    main(server=args.server, port=int(args.port), default_size=int(args.size), mode=args.mode)
