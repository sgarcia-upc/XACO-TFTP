import random

PORT_MIN = 49152
PORT_MAX = 65535

def generateTID():
    return random.randint(PORT_MIN, PORT_MAX)


