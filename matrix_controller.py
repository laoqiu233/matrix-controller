import smbus

def get_binary_int8(num):
    """Returns the correct binary form of any number
    (For negative numbers)
    
    Args:
        num (int): The number to convert

    Returns:
        int: The correct binary form of this number
    """
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
    
    def get_info(self):
        """Returns basic information about the controller
        Can be used for verification purposes.

        Returns:
            str: Controller version. Should always be in form of 'Vn.m    '
            str: Manufacturer. Should always be 'HiTechnc'
            str: Controller type. Should always be 'M4S4cont'
        """
        version = ''.join(map(chr, self.bus.read_i2c_block_data(self.addr, 0x00, 8)))
        manufacturer = ''.join(map(chr, self.bus.read_i2c_block_data(self.addr, 0x08, 8)))
        controller_type = ''.join(map(chr, self.bus.read_i2c_block_data(self.addr, 0x10, 8)))

        return (version, manufacturer, controller_type)

    def get_status(self):
        """Returns status of the controller.
        Including controller failure, battery status.

        Returns:
            bool: batt_low
            bool: fault
            int: battery_level
            In units of 40mV
        """

        status = self.bus.read_byte_data(self.addr, 0x41)
        batt_low = bool(status & 0x02)
        fault = bool(status &0x01)
        battery_level = self.bus.read_byte_data(self.addr, 0x43)

        return (batt_low, fault, battery_level)

if __name__ == '__main__':
    """Testing"""
    matrix = Controller(1, 0x08)
    print(matrix.get_info())
    print(matrix.get_status())