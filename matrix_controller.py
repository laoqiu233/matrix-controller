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
    """Class for the matrix controller
    Attributes:
        addr(int): Controller's I2C address
        bus(smbus.SMBus): I2C bus
    """

    def __init__(self, bus, addr):
        """Creates a controller instance
        Args:
            addr(int): Controller's I2C address
            bus(int): Which I2C bus to use for the controller
        """
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

    def set_timeout(self, seconds):
        """Sets the timeout for automatic servo/motor shutdown
        If the input arguments is -1, it simply returns the current timeout value.

        Args:
            seconds(int): How many seconds the timeout should last.
            |-1 <= seconds <= 255|

        Returns:
            int: The timeout set on the controller.
        """

        assert -1 <= seconds <= 255

        if seconds > -1:
            self.bus.write_byte_data(self.addr, 0x42, seconds)
        return self.bus.read_byte_data(self.addr, 0x42)

if __name__ == '__main__':
    """Testing"""
    matrix = Controller(1, 0x08)
    print(matrix.get_info())
    print(matrix.get_status())
    print(matrix.set_timeout(20))