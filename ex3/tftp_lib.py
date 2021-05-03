import random

PORT_MIN = 49152
PORT_MAX = 65535

def generateTID():
    return random.randint(PORT_MIN, PORT_MAX)

def send_file(socket, server, port, filename, size):
    try:
        f = open(filename, "rb")
        data = f.read(size)
        print("enviando... %s" %len(data))
        while (len(data) > 0):
            if (socket.sendto(data, (server, port))):
                if(len(data) == size):
                    data = f.read(size)
                    if (len(data) == 0): # Si es un fichero multiplo de size enviamos un paquete con 0 bytes de datos para comunicar al cliente que hemos acabado
                        socket.sendto(data, (server, port))
                else:
                    data = bytes()
            print("enviando... %s" %len(data))
    except IOError as e:
        print("File requested not found")
        print(e)
    finally:
        try:
            f.close()
        except:
            pass

def recv_file(socket, filename, size):
    """
    esperamos los data y enviamos ack cuando los recibimos
    """
    data, addr = socket.recvfrom(size)
    print(" recibiendo... %s" %len(data))
    try:
        f = open(filename, "wb")
        
        while (data):
            f.write(data)
            
            if (len(data) == size):
                # Vamos a pedir mas datos en caso de que los haya
                data, addr = socket.recvfrom(size)
            else:
                data = bytes()
            print(" recibiendo... %s" %len(data))
            
    except IOError:
        print("File requested not found")
    except timeout:
        print("timeout")
    finally:
        try:
            f.close()
        except:
            pass
