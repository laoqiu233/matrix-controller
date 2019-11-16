import smbus

def get_binary_int8(num):
    if num >= 0:
        return num
    else:
        num = num ^ 0xFF
        num += 1
        return num & 0xFF

class Controller:

    def __init__(self, bus, addr):
        self.addr = addr
        self.bus = smbus.SMBus(bus)
    