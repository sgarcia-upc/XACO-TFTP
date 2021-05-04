#!/usr/bin/env python3
import sys
import time
import argparse
import tftp_lib
import tftp_pkg as pkg

from socket import *

def main(port=12000, size=512):

    # Setup IPv4 UDP socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)

    # Specify the welcoming port of the server
    serverSocket.bind(('', port))

    print ("Esperando conexiones...")
    while True:
        message, clientAddress = serverSocket.recvfrom(size)
        op_code = pkg.decodificate_opcode(message)

        print("Client connected {} -- {} ".format(clientAddress, op_code), end='')
        if (op_code == "RRQ"):
            filename, mode = pkg.decodificate_rrq(message)
            print("GET /{}".format(filename))
            print(clientAddress)
            tftp_lib.send_file(serverSocket, clientAddress[0], clientAddress[1], filename, size, mode)

        elif (op_code == "WRQ"):
            filename, mode = pkg.decodificate_wrq(message)
            print("PUT {}".format(filename))
            
            ack = pkg.generate_ack(0)
            serverSocket.sendto(ack, clientAddress)
            print("sending ACK: 0")

            tftp_lib.recv_file(serverSocket, clientAddress[0], clientAddress[1], filename, size, mode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port', help='Puerto destino', default=12000)
    parser.add_argument('--size', help='Tamaño paquete', default=512)
    args = parser.parse_args()

    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(port=int(args.port), size=int(args.size))
