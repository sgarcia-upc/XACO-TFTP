#!/usr/bin/env python3
import sys
import time
import threading
import argparse
sys.path.append("../lib/")
import tftp_lib
import tftp_pkg as pkg

from socket import *


def rrq_worker(message, size, tid_port, clientAddress):
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', tid_port))

    filename, mode, option_list = pkg.decodificate_rrq(message)
    print("GET /{} {}".format(filename, mode))
    print(clientAddress)
    print("TID: %s"%tid_port)

    blksize = None
    decided_size = size
    for i in range(0, len(option_list), 2):
        if option_list[i] == "blksize":
            print ("Option detectet: {} with value {}".format(option_list[i], option_list[i+1]))
            blksize = option_list[i+1]

    if blksize != None:
        oack = pkg.generate_oack()
        oack = pkg.add_oack_option(oack, "blksize", blksize)
        decided_size = int(blksize)
        serverSocket.sendto(oack, clientAddress)
        print("sending OACK with blksize = {}".format(blksize))

        msg, addr = serverSocket.recvfrom(tftp_lib.RCV_SIZE) # recibimos ack0
        block_num_ack = pkg.decodificate_ack(msg)       # decode
        print("receiving ACK: %s from %s:%s"%(block_num_ack, addr[0], addr[1]))

    try:
        tftp_lib.send_file(serverSocket, clientAddress[0], clientAddress[1], filename, decided_size, mode)
    except tftp_lib.DiskFull as e:
        print("ERROR: {}".format(e))
    except tftp_lib.UnknownException as e:
        print("ERROR: {}".format(e))
    except IOError as e:
        print("Sending error FileNotFound")
        err = pkg.generate_err("FileNotFound", "Server: we can't found file: '{}'".format(filename))
        serverSocket.sendto(err, clientAddress)

    try:
        serverSocket.close()
    except:
        pass

def rrw_worker(message, size, tid_port, clientAddress):
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', tid_port))
    filename, mode, option_list = pkg.decodificate_wrq(message)
   
    print("PUT /{} {}".format(filename, mode))
    print(clientAddress)
    print("TID: %s"%tid_port)
    blksize = None
    decided_size = size
    for i in range(0, len(option_list), 2):
        if option_list[i] == "blksize":
            print ("Option detectet: {} with value {}".format(option_list[i], option_list[i+1]))
            blksize = option_list[i+1]

    if blksize == None:
        ack = pkg.generate_ack(0)
        serverSocket.sendto(ack, clientAddress)
        print("sending ACK: 0")
    else:
        oack = pkg.generate_oack()
        oack = pkg.add_oack_option(oack, "blksize", blksize)
        decided_size = int(blksize)
        serverSocket.sendto(oack, clientAddress)
        print("sending OACK with blksize = {}".format(blksize))
        
    try:
        tftp_lib.recv_file(serverSocket, clientAddress[0], clientAddress[1], filename, decided_size, mode)
    except tftp_lib.FileNotFound as e:
        print(e)

    try:
        serverSocket.close()
    except:
        pass

def main(port=12000, size=512):

    # Setup IPv4 UDP socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)

    threads = []

    # Specify the welcoming port of the server
    serverSocket.bind(('', port))

    print ("Esperando conexiones...")
    while True:
        message, clientAddress = serverSocket.recvfrom(tftp_lib.RCV_SIZE)
        op_code = pkg.decodificate_opcode(message)

        print("Client connected {} -- {} ".format(clientAddress, op_code), end='')
        if (op_code == "RRQ"):
            port = tftp_lib.generateTID()
            t = threading.Thread(target=rrq_worker, args=(message, size, port , clientAddress, ))
            threads.append(t)
            t.daemon = True
            t.start()

        elif (op_code == "WRQ"):
            port = tftp_lib.generateTID()
            t = threading.Thread(target=rrw_worker, args=(message, size, port, clientAddress, ))
            threads.append(t)
            t.daemon = True
            t.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port', help='Puerto destino', default=12000)
    parser.add_argument('--size', help='Tamaño paquete', default=512)
    args = parser.parse_args()

    if (int(args.port) < 0 or int(args.port) > 2**16-1):
        print("El puerto debe ser un numero desde el 0 al {}".format(2**16-1))
        sys.exit(1)

    main(port=int(args.port), size=int(args.size))
