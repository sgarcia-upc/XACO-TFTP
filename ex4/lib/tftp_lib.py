import random
import os
import sys
import tftp_pkg as pkg

# Lista de excepciones usadas en el tftp
class FileNotFound(Exception):
    pass

class DiskFull(Exception):
    pass

class UnknownException(Exception):
    pass

PORT_MIN = 49152
PORT_MAX = 65535
RCV_SIZE = 512

def generateTID():
    """
    RETORNA un numero random desde PORT_MIN HASTA PORT_MAX
    """
    return random.randint(PORT_MIN, PORT_MAX)


def send_file(socket, server, port, filename, size, modo):
    """
        Funcion generica para enviar un fichero

        socket: conexion viva con el cliente/server
        server: ip del server/cliente
        port:   puerto del server/cliente
        filename: path del fichero a transmitir
        size: tamaño de los paquetes de data
        modo: metodo de transmission del fichero
    """
    
    if modo=="netascii":
        m = "r"
    elif modo=="octet":
        m = "rb"
    else:
        print("NoSuchMODO")
        sys.exit(1)

    with open(filename, m) as f:
        block_num_ack = 0
        block_num = 1
        file_data = f.read(size)

        data = pkg.generate_data(block_num, file_data)
        while (len(file_data) > 0):

            while(block_num != block_num_ack):
                socket.sendto(data, (server, port))
                print("sending DATA: %s -- %s"%(block_num, len(file_data)))        
                ack, addr = socket.recvfrom(RCV_SIZE)
                if pkg.decodificate_opcode(ack) == "ACK":
                    block_num_ack =  pkg.decodificate_ack(ack)
                    print("receiving ACK: {} from {}:{}".format(block_num_ack, addr[0], addr[1]))
                elif pkg.decodificate_opcode(ack) == "ERR":
                    err_code, msg = pkg.decodificate_err(ack)
                    if (err_code == "DiskFull"):
                        raise DiskFull(msg)
                    else:
                        raise UnknownException(msg)
                    

            block_num+=1
            block_num = block_num % 65535
            if(block_num == 0):
                block_num = 1

            if(len(file_data) == size):
                file_data = f.read(size)
                data = pkg.generate_data(block_num, file_data)
                if (len(file_data) == 0): 
                    while(block_num != block_num_ack):
                        socket.sendto(data, (server, port))
                        print("sending DATA: %s -- %s"%(block_num, len(file_data)))
                        ack, addr = socket.recvfrom(RCV_SIZE)
                        block_num_ack =  pkg.decodificate_ack(ack)
                        print("receiving ACK: {} from {}:{}".format(block_num_ack, addr[0], addr[1]))
                    block_num+=1
                    block_num = block_num % 65535
                    if(block_num == 0):
                        block_num = 1
            else:
                file_data = bytes()
                    
            
   

def recv_file(socket, server, port, filename, size, modo, data=None):
    """
        Funcion generica para recibit un fichero 


        socket: conexion viva con el cliente/server
        server: ip del server/cliente
        port:   puerto del server/cliente
        filename: path del fichero a transmitir
        size: tamaño de los paquetes de data
        modo: metodo de transmission del fichero
        data: De existir significara que el cliente/server ya recibio el data1 
    """
    if data == None:
        data, addr = socket.recvfrom(4+size)
    else:
        addr = (server, port)

    pkg_type = pkg.decodificate_opcode(data)
    if pkg_type == "DATA":
        num_block, file_data = pkg.decodificate_data(data)
    elif pkg_type == "ERR":
        pkg_type, msg = pkg.decodificate_err(data)
        raise FileNotFound(msg)
        
    data = file_data
    if modo == "netascii":
        data = file_data.decode("ascii")

    print("receiving DATA: {} -- {} from {}:{}".format(num_block, len(file_data), addr[0], addr[1]))
    ack = pkg.generate_ack(num_block)
    socket.sendto(ack, (server, port))
    print("sending ACK: %s"%(num_block))
 
    try:
        if modo=="netascii":
            f = open(filename, "w")
        elif modo=="octet":
            f = open(filename, "wb")
        else:
            print("NoSuchMODO")
            sys.exit(1)
        
        while (file_data):
            f.write(data)
            
            if (len(file_data) == size):
                # Vamos a pedir mas datos en caso de que los haya
                data, addr = socket.recvfrom(4+size)
                num_block, file_data = pkg.decodificate_data(data)
                data = file_data
                if modo == "netascii":
                    data = file_data.decode("utf-8")

                print("receiving DATA: {} -- {} from {}:{}".format(num_block, len(file_data), addr[0], addr[1]))
                ack = pkg.generate_ack(num_block)
                socket.sendto(ack, (server, port))
                print("sending ACK: %s"%(num_block))
            else:
                file_data = bytes()

    except OSError as e:
        if (e.args[0] == 28): # No space left on device
            # Recogemos el dato que no cabe
            data, addr = socket.recvfrom(4+size)
            os.remove(filename)
            msg = pkg.generate_err("DiskFull", e.args[1])
            socket.sendto(msg, (server,port))
            print("Sending ERROR: DiskFull")
         
    except IOError:
        print("File requested not found")
    finally:
        try:
            f.close()
        except:
            pass
