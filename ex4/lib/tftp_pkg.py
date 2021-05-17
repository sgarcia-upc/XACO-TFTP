import struct

transmission_mode = ["netascii", "octet"]
"""
Los dos primeros bytes del paquetes nos indican el tipo de paquete que és
"""
op_codes = {
    "RRQ" : struct.pack('BB', 0, 1),
    "WRQ" : struct.pack('BB', 0, 2),
    "DATA": struct.pack('BB', 0, 3),
    "ACK" : struct.pack('BB', 0, 4),
    "ERR" : struct.pack('BB', 0, 5),
    "OACK" : struct.pack('BB', 0, 6),
}

"""
El byte de 2 al 4 nos indican el tipo de error que tenemos
"""
err_codes = {
    "NotDefined"        : struct.pack('BB', 0, 1),
    "FileNotFound"      : struct.pack('BB', 0, 2),
    "AccesViolation"    : struct.pack('BB', 0, 3),
    "DiskFull"          : struct.pack('BB', 0, 4),
    "IllegalOperation"  : struct.pack('BB', 0, 5),
    "FileAlredyExist"   : struct.pack('BB', 0, 6),
    "NoSuchUser"        : struct.pack('BB', 0, 7),
}

"""
Nos indica el tipo de paquete a traves del op_codes i el err_codes 
"""
def find_key_by_value(d,val):
    for key, value in d.items():
         if val == value:
             return key
    return -1

"""
Genereamos el paquete del RRQ con 2 bytes de op_code, un string con el nombre del paquete, un byte a zero, el modo(netascii/octet) i otro byte a zero que indica el final del paquete.
"""
def generate_rrq_rrw_pkg(op, filename, mode):
    pkg = op_codes[op]
    pkg = pkg + bytes(to_str(filename), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    pkg = pkg + bytes(to_str(mode), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    return pkg
    
"""
A un paquete le añadimos una opción inidcando el nombre de la opción con un string, un byte a zero, el valor de la opción i otro byte a zero para indicar el final del paquete.
"""    
def add_option_rrq_wrq(pkg, option_name, value):
    pkg = pkg + bytes(to_str(option_name), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    pkg = pkg + bytes(to_str(value), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    return pkg
    
"""
Convertimos un valor en string para el paquete.
""" 
def to_str(value):
    if isinstance(value, int):
        value = int(value)
    #if not isinstance(value, str):
        value = str(value)
    return value

"""
Decodfificamos el op_code de un paquete
"""
def decodificate_opcode(pkg):
    op_code = struct.pack('BB', 0, pkg[0] + pkg[1])
    op_code = find_key_by_value(op_codes, op_code)
    return op_code

"""
Genereamos el paquete RRQ 
"""
# RRQ       | 2bytes  |     string     | 1byte | string | 1byte
#           | op code | nombre fichero |   0   |  modo  |   0
def generate_rrq(filename, mode):
    return generate_rrq_rrw_pkg("RRQ", filename, mode)

"""
Decodfificamos un paquete RRQ y nos retorna el nombre del fitxero , el modo y si tiene opciones, una lista de las que contiene.
"""
def decodificate_rrq(pkg):
    filename = ""
    mode = ""
    last = 2
    option_list = []
    option = ""
    for byte in pkg[last:]:
        last += 1
        if (byte == 0):
            break

        filename += chr(byte)

    for byte in pkg[last:]:
        last += 1
        if (byte == 0):
            break

        mode += chr(byte)
        
    for byte in pkg[last:]:
        last += 1
        if (byte == 0):
            option_list.append(option)
            option = ""
        else:
            option += chr(byte)

    return filename, mode, option_list

"""
Genereamos el paquete WRQ
"""
# WRQ       | 2bytes  |     string     | 1byte | string | 1byte
#           | op code | nombre fichero |   0   |  modo  |   0
def generate_wrq(filename, mode):
    return generate_rrq_rrw_pkg("WRQ", filename, mode)

"""
Decodfificamos un paquete WRQ y nos retorna el nombre del fitxero , el modo y si tiene opciones, una lista de las que contiene.
"""
def decodificate_wrq(pkg):
    filename, mode, option_list = decodificate_rrq(pkg)
    return filename, mode, option_list


"""
Genereamos el paquete DATA 
"""
# DATA      | 2bytes  |     2bytes     | nBytes |
#           | op code |  numero bloque |  data |
def generate_data(nck, data):
    pkg = op_codes["DATA"]
    pkg = pkg + struct.pack('>H', nck)
    if (isinstance(data, str)):
        pkg = pkg + data.encode("ascii")
    else:
        pkg = pkg + data
    return pkg

"""
Decodfificamos un paquete DATA y nos retona el numero de bloque y los datas.
"""
def decodificate_data(pkg):
    num_block = pkg[3]|pkg[2]<<8
    data = pkg[4:]
        
    return num_block, data


# ACK       | 2bytes  |     2bytes      |
#           | op code |  numero bloque  |
def generate_ack(nck):
    pkg = op_codes["ACK"]
    pkg = pkg + struct.pack('>H', nck)
    return pkg

"""
Decodfificamos un paquete ACK i nos retona el numero de bloque.
"""
def decodificate_ack(pkg):
    num_block = pkg[3]|pkg[2]<<8
    return num_block

"""
La usamos para printar los paquetes en hexadecimal sin interpretación de carácteres.
"""
def print_pkg_in_hex(pkg):
    i = 0
    for x in bytearray(pkg).hex():
        if i % 2 == 0:
            print("\\x", end="")
        print(x.upper(), end="")
        i+=1
    print()

"""
Genereamos el paquete DATA 
"""
# ERR     |  2bytes  |  2bytes  |     string     |  1byte  |
#         |  op code | err code | nombre fichero |    0    |
def generate_err(err_code, msg):
    pkg = op_codes["ERR"]
    pkg = pkg + err_codes[err_code]
    pkg = pkg + bytes(msg, "utf-8")
    pkg = pkg + struct.pack('B', 0)
    return pkg;

"""
Decodfificamos un paquete ERR y nos devuelve su codigo de error y el mensaje que indica que error es.
"""
def decodificate_err(pkg):
    err_code = struct.pack('BB', 0, pkg[2] + pkg[3])
    err_code = find_key_by_value(err_codes, err_code)
    msg = ""
    for byte in pkg[4:]:
        if (byte == 0):
            break

        msg += chr(byte)
    return err_code, msg

"""
Genereamos el paquete OACK
"""
# OACK       | 2bytes  |
#            | op code |
def generate_oack():
    pkg = op_codes["OACK"]
    return pkg

"""
Decodfificamos un paquete OACK y nos devuelve una lista con las opciones que contiene.
"""
def decodificate_oack(pkg):
    last = 2
    option_list = []
    option = ""
        
    for byte in pkg[last:]:
        last += 1
        if (byte == 0):
            option_list.append(option)
            option = ""
        else:
            option += chr(byte)

    return option_list

"""
Añade una opción a un RRQ o WRQ. Le añade alfinal del paquete el nombre de la opción un byte a zero, el valor de la opción y otro byte a zero que indica el final del paquete.
Retornamos el paquete con la sopciones añadidas.
"""
# RRQ/WRQ       | 2bytes  |     string     | 1byte | string | 1byte |   option_name   | 1byte | value | 1byte |
#               | op code | nombre fichero |   0   |  modo  |   0   |  nombre opcion  |   0   | valor |   0   |
def add_oack_option(pkg, option_name, value):
    pkg = add_option_rrq_wrq(pkg, option_name, value)
    return pkg

"""
Ejemplos de uso de la librería.
Al improtar la libreria non se ejecuta esta parte del código.
"""
if __name__ == "__main__":
    pkg = generate_rrq("meh.txt", transmission_mode[0])
    pkg = add_option_rrq_wrq(pkg, "blksize", "512")
    # ~ pkg = generate_data(44, "klashdfkhasdkjfh")
    # ~ pkg = generate_ack(30001)
    # ~ pkg = generate_err("FileNotFound","meh.txt no ta")
    op_code = decodificate_opcode(pkg)
    if op_code == "RRQ":
        filename, mode, option_list = decodificate_rrq(pkg)
        print("RRQ: %s -- %s"%(filename, mode))
        for option in option_list:
            print("-- {}".format(option))
    elif op_code == "WRQ":
        filename, mode, option_list = decodificate_wrq(pkg)
        print("WRQ: %s -- %s"%(filename, mode))
        for option in option_list:
            print(option)
    elif op_code == "DATA":
        num_block, data = decodificate_data(pkg)
        print("DATA: %s -- %s"%(num_block, data))
    elif op_code == "ACK":
        num_block = decodificate_ack(pkg)
        print("ACK: %s"%(num_block))
    elif op_code == "OACK":
        num_block = decodificate_oack(pkg)
        print("ACK: %s"%(num_block))
    elif op_code == "ERR":
        err_code, msg = decodificate_err(pkg)
        print("ERR: %s -- %s"%(err_code, msg))
