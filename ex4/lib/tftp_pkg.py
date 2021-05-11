import struct

transmission_mode = ["netascii", "octet"]
op_codes = {
    "RRQ" : struct.pack('BB', 0, 1),
    "WRQ" : struct.pack('BB', 0, 2),
    "DATA": struct.pack('BB', 0, 3),
    "ACK" : struct.pack('BB', 0, 4),
    "ERR" : struct.pack('BB', 0, 5),
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
    pkg = pkg + bytes(filename, "utf-8")
    pkg = pkg + struct.pack('B', 0)
    pkg = pkg + bytes(mode, "utf-8")
    pkg = pkg + struct.pack('B', 0)
    return pkg


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


# WRQ       | 2bytes  |     string     | 1byte | string | 1byte
#           | op code | nombre fichero |   0   |  modo  |   0
def generate_wrq(filename, mode):
    return generate_rrq_rrw_pkg("WRQ", filename, mode)


def decodificate_wrq(pkg):
    filename, mode = decodificate_rrq(pkg)
    return filename, mode


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


if __name__ == "__main__":
    pkg = generate_rrq("meh.txt", transmission_mode[0])
    pkg = generate_data(44, "klashdfkhasdkjfh")
    pkg = generate_ack(30001)
    pkg = generate_err("FileNotFound","meh.txt no ta")
    op_code = decodificate_opcode(pkg)
    if op_code == "RRQ":
        filename, mode = decodificate_rrq(pkg)
        print("RRQ: %s -- %s"%(filename, mode))
    elif op_code == "WRQ":
        filename, mode = decodificate_wrq(pkg)
        print("WRQ: %s -- %s"%(filename, mode))
    elif op_code == "DATA":
        num_block, data = decodificate_data(pkg)
        print("DATA: %s -- %s"%(num_block, data))
    elif op_code == "ACK":
        num_block = decodificate_ack(pkg)
        print("ACK: %s"%(num_block))
    elif op_code == "ERR":
        err_code, msg = decodificate_err(pkg)
        print("ERR: %s -- %s"%(err_code, msg))
