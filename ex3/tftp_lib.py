import random
import sys
import tftp_pkg as pkg

PORT_MIN = 49152
PORT_MAX = 65535

def generateTID():
    return random.randint(PORT_MIN, PORT_MAX)

def send_file(socket, server, port, filename, size, modo):
    try:
        if modo=="netascii":
            f = open(filename, "r")
        elif modo=="octet":
            f = open(filename, "rb")
        else:
            print("NoSuchMODO")
            sys.exit(1)

        block_num = 1
        file_data = f.read(size)
        data = pkg.generate_data(block_num, file_data)
        print("enviando... %s" %len(file_data))
        # TODO: if file is empty
        while (len(file_data) > 0):
            if (socket.sendto(data, (server, port))):
                # TODO: CHECK ACK
                if(len(file_data) == size):
                    file_data = f.read(size)
                    block_num+=1
                    data = pkg.generate_data(block_num, file_data)
                    if (len(file_data) == 0): 
                        socket.sendto(data, (server, port))
                else:
                    file_data = bytes()

            print("enviando... %s" %len(file_data))
    except IOError as e:
        print("File requested not found")
        print(e)
    finally:
        try:
            f.close()
        except:
            pass

def recv_file(socket, filename, size, modo):
    """
    esperamos los data y enviamos ack cuando los recibimos
    """
    data, addr = socket.recvfrom(4+size)
    #TODO: mirar si el data tiene op_code data...
    num_block, file_data = pkg.decodificate_data(data)
    #TODO: enviar ACK

    print(" recibiendo... %s" %len(file_data))
    try:
        if modo=="netascii":
            f = open(filename, "w")
        elif modo=="octet":
            f = open(filename, "wb")
        else:
            print("NoSuchMODO")
            sys.exit(1)
        
        while (file_data):
            f.write(file_data)
            
            if (len(file_data) == size):
                # Vamos a pedir mas datos en caso de que los haya
                data, addr = socket.recvfrom(4+size)
                #TODO: mirar si el data tiene op_code data...
                num_block, file_data = pkg.decodificate_data(data)
                #TODO: enviar ACK
            else:
                file_data = bytes()
            print(" recibiendo... %s" %len(file_data))
            
    except IOError:
        print("File requested not found")
    except timeout:
        print("timeout")
    finally:
        try:
            f.close()
        except:
            pass
