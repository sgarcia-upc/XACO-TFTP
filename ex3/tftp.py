import random
import struct 

PORT_MIN = 49152
PORT_MAX = 65535

def generateTID():
    return random.randint(PORT_MIN, PORT_MAX)

transmission_mode = ["netascii", "octet"]
op_codes = {
    "RRQ" : struct.pack('BB', 0, 1), #RRQ
    "WRQ" : struct.pack('BB', 0, 2), #WRQ
    "DATA": struct.pack('BB', 0, 3),#DATA
    "ACK" : struct.pack('BB', 0, 4), #ACK
    "ERR" : struct.pack('BB', 0, 5), #ERR
}

def find_key_by_value(d,val):
    for key, value in d.items():
         if val == value:
             return key
    return -1


# RRQ/WRQ = | 2bytes  |     string     | 1byte | string | 1byte
#           | op code | nombre fichero |   0   |  modo  |   0

def generate_rrq_rrw_pkg(op, filename, mode):
    pkg = op_codes[op]  
    pkg = pkg + bytes(filename, "utf-8")
    pkg = pkg + struct.pack('B', 0) 
    pkg = pkg + bytes(mode, "utf-8")
    pkg = pkg + struct.pack('B', 0) 
    return pkg

def decodificate_opcode(pkg):
    op_code = struct.pack('BB', 0, pkg[0] + pkg[1])
    op_code = find_key_by_value(op_codes, op_code)
    return op_code

def generate_rrq(filename, mode):
    return generate_rrq_rrw_pkg("RRQ", filename, mode)

def decodificate_rrq(pkg):
    filename = ""
    mode = ""
    last = 2
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

    return filename, mode

def generate_wrq(filename, mode):
    return generate_rrq_rrw_pkg("WRQ", filename, mode)

def decodificate_wrq(pkg):
    return decodificate_rrq

def generate_data(nck, data):
    #pkg = op_codes["DATA"]  
    pkg =  struct.pack('>H', int(nck))
    print(type(pkg))
    print(bytes(pkg))
    #pkg = pkg + bytes(data, "utf-8")

def decodificate_data(pkg):
    num_block = pkg[2] + pkg[3]
    data = pkg[4:]
    return num_block, data


#pkg = generate_rrq("meh.txt", transmission_mode[0])
pkg = generate_data(44, "klashdfkhasdkjfh")
#op_code = decodificate_opcode(pkg)

#print(op_code)
#if op_code == "RRQ":
#    filename, mode = decodificate_rrq(pkg)
#elif op_code == "WRQ":
#    filename, mode = decodificate_wrq(pkg)
#elif op_code == "DATA":
#    num_block, data = decodificate_data(pkg) 
#    print("DATA: %s -- %s".format(num_block, data))
