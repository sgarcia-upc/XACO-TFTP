import random
import os
import sys
import tftp_pkg as pkg

class FileNotFound(Exception):
    pass

class DiskFull(Exception):
    pass

class UnknownException(Exception):
    pass

PORT_MIN = 49152
PORT_MAX = 65535

def generateTID():
    return random.randint(PORT_MIN, PORT_MAX)


def send_file(socket, server, port, filename, size, modo):
    
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
                ack, add = socket.recvfrom(512)
                if pkg.decodificate_opcode(ack) == "ACK":
                    block_num_ack =  pkg.decodificate_ack(ack)
                    print("receiving ACK: %s"%(block_num_ack))
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
                        ack, add = socket.recvfrom(4)
                        block_num_ack =  pkg.decodificate_ack(ack)
                        print("receiving ACK: %s"%(block_num_ack))
                    block_num+=1
                    block_num = block_num % 65535
                    if(block_num == 0):
                        block_num = 1
            else:
                file_data = bytes()
                    
            
   

def recv_file(socket, server, port, filename, size, modo, data=None):
    """
    esperamos los data y enviamos ack cuando los recibimos
    """
    if data == None:
        data, addr = socket.recvfrom(4+size)

    pkg_type = pkg.decodificate_opcode(data)
    if pkg_type == "DATA":
        num_block, file_data = pkg.decodificate_data(data)
    elif pkg_type == "ERR":
        pkg_type, msg = pkg.decodificate_err(data)
        raise FileNotFound(msg)
        
    data = file_data
    if modo == "netascii":
        data = file_data.decode("ascii")

    print("receiving DATA: %s -- %s"%(num_block, len(file_data)))
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
            # TODO: calcular si queda espacio
            # si queda menos de len(data)
            f.write(data)
            
            if (len(file_data) == size):
                # Vamos a pedir mas datos en caso de que los haya
                data, addr = socket.recvfrom(4+size)
                #TODO: mirar si el data tiene op_code data...
                num_block, file_data = pkg.decodificate_data(data)
                data = file_data
                if modo == "netascii":
                    data = file_data.decode("utf-8")

                print("receiving DATA: %s -- %s"%(num_block, len(file_data)))
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
