import struct

transmission_mode = ["netascii", "octet"]
op_codes = {
    "RRQ" : struct.pack('BB', 0, 1),
    "WRQ" : struct.pack('BB', 0, 2),
    "DATA": struct.pack('BB', 0, 3),
    "ACK" : struct.pack('BB', 0, 4),
    "ERR" : struct.pack('BB', 0, 5),
    "OACK" : struct.pack('BB', 0, 6),
}


err_codes = {
    "NotDefined"        : struct.pack('BB', 0, 1),
    "FileNotFound"      : struct.pack('BB', 0, 2),
    "AccesViolation"    : struct.pack('BB', 0, 3),
    "DiskFull"          : struct.pack('BB', 0, 4),
    "IllegalOperation"  : struct.pack('BB', 0, 5),
    "FileAlredyExist"   : struct.pack('BB', 0, 6),
    "NoSuchUser"        : struct.pack('BB', 0, 7),
}


def find_key_by_value(d,val):
    for key, value in d.items():
         if val == value:
             return key
    return -1


def generate_rrq_rrw_pkg(op, filename, mode):
    pkg = op_codes[op]
    pkg = pkg + bytes(to_str(filename), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    pkg = pkg + bytes(to_str(mode), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    return pkg
    
def add_option_rrq_wrq(pkg, option_name, value):
    pkg = pkg + bytes(to_str(option_name), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    pkg = pkg + bytes(to_str(value), "utf-8")
    pkg = pkg + struct.pack('B', 0)
    return pkg
    
def to_str(value):
    if isinstance(value, int):
        value = int(value)
    #if not isinstance(value, str):
        value = str(value)
    return value

def decodificate_opcode(pkg):
    op_code = struct.pack('BB', 0, pkg[0] + pkg[1])
    op_code = find_key_by_value(op_codes, op_code)
    return op_code


# RRQ       | 2bytes  |     string     | 1byte | string | 1byte
#           | op code | nombre fichero |   0   |  modo  |   0
def generate_rrq(filename, mode):
    return generate_rrq_rrw_pkg("RRQ", filename, mode)


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


# WRQ       | 2bytes  |     string     | 1byte | string | 1byte
#           | op code | nombre fichero |   0   |  modo  |   0
def generate_wrq(filename, mode):
    return generate_rrq_rrw_pkg("WRQ", filename, mode)


def decodificate_wrq(pkg):
    filename, mode, option_list = decodificate_rrq(pkg)
    return filename, mode, option_list


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


def decodificate_data(pkg):
    num_block = pkg[3]|pkg[2]<<8
    data = pkg[4:]
        
    return num_block, data


# DATA      | 2bytes  |     2bytes      |
#           | op code |  numero bloque  |
def generate_ack(nck):
    pkg = op_codes["ACK"]
    pkg = pkg + struct.pack('>H', nck)
    return pkg


def decodificate_ack(pkg):
    num_block = pkg[3]|pkg[2]<<8
    return num_block


def print_pkg_in_hex(pkg):
    i = 0
    for x in bytearray(pkg).hex():
        if i % 2 == 0:
            print("\\x", end="")
        print(x.upper(), end="")
        i+=1
    print()


# WRQ     |  2bytes  |  2bytes  |     string     |  1byte  |
#         |  op code | err code | nombre fichero |    0    |
def generate_err(err_code, msg):
    pkg = op_codes["ERR"]
    pkg = pkg + err_codes[err_code]
    pkg = pkg + bytes(msg, "utf-8")
    pkg = pkg + struct.pack('B', 0)
    return pkg;


def decodificate_err(pkg):
    err_code = struct.pack('BB', 0, pkg[2] + pkg[3])
    err_code = find_key_by_value(err_codes, err_code)
    msg = ""
    for byte in pkg[4:]:
        if (byte == 0):
            break

        msg += chr(byte)
    return err_code, msg

def generate_oack():
    pkg = op_codes["OACK"]
    return pkg

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

def add_oack_option(pkg, option_name, value):
    pkg = add_option_rrq_wrq(pkg, option_name, value)
    return pkg


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
