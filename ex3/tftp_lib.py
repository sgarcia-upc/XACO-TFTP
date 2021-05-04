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
            m = "r"
        elif modo=="octet":
            m = "rb"
        else:
            print("NoSuchMODO")
            sys.exit(1)

        with open(filename, "rb") as f:
            block_num_ack = 0
            block_num = 65534
            file_data = f.read(size)
            data = pkg.generate_data(block_num, file_data)
            # TODO: if file is empty
            while (len(file_data) > 0):

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
                    #while(block_num != block_num_ack):
                    #        socket.sendto(data, (server, port))
                    #        ack, add = socket.recvfrom(4)
                    #        block_num_ack =  pkg.decodificate_ack(ack)
                    #        print("receiving ACK: %s"%(block_num_ack))
                    
            
    except IOError as e:
        print("File requested not found")
        print(e)

def recv_file(socket, server, port, filename, size, modo):
    """
    esperamos los data y enviamos ack cuando los recibimos
    """
    data, addr = socket.recvfrom(4+size)
    #TODO: mirar si el data tiene op_code data...   
    num_block, file_data = pkg.decodificate_data(data)
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
            f.write(file_data)
            
            if (len(file_data) == size):
                # Vamos a pedir mas datos en caso de que los haya
                data, addr = socket.recvfrom(4+size)
                #TODO: mirar si el data tiene op_code data...
                num_block, file_data = pkg.decodificate_data(data)
                print("receiving DATA: %s -- %s"%(num_block, len(file_data)))
                ack = pkg.generate_ack(num_block)
                socket.sendto(ack, (server, port))
                print("sending ACK: %s"%(num_block))
            else:
                file_data = bytes()
            
            
    except IOError:
        print("File requested not found")
    except timeout:
        print("timeout")
    finally:
        try:
            f.close()
        except:
            pass
