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

    servo_registers = [
        0x46,
        0x48,
        0x50,
        0x52,
    ]

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

        if not -1 <= seconds <= 255:
            raise ValueError('The timeout should be in the range of [-1, 255].')

        if seconds > -1:
            self.bus.write_byte_data(self.addr, 0x42, seconds)
        return self.bus.read_byte_data(self.addr, 0x42)

    def set_servos(self, servos):
        """Controls the generation of servo control pulses.

        Args:
            servos(list): State to change to for each servo
                          If the element is -1, then it does nothing to the servo.
                          If the element is 0, then it disables the servo.
                          If the element is 1, then it enables the servo
        
        Returns:
            list: The state of each servo
                  False - disabled
                  True - enabled
        """

        val = self.bus.read_byte_data(self.addr, 0x45)

        if len(servos) != 4: raise ValueError('The length of the list should be exactly 4.')
        for index in range(4):
            if not -1 <= servos[index] <= 1: raise ValueError('Element %s has a inappropriate value.' %index)
            if servos[index] == -1: continue
            elif servos[index] == 0: val &= (1 << index) ^ 0xFF
            else: val |= 1 << index

        self.bus.write_byte_data(self.addr, 0x45, val)
        val = self.bus.read_byte_data(self.addr, 0x45)
        
        return [(val & (1 << index)) > 0 for index in range(4)]
    
    def set_servo_speed(self, servo, speed):
        """Sets the speed for the servo.
        The servo's speed is the rate, at which changes to the servo positions
        are made.
        If the value is set to zero, changes to the servo position is immediate. 
        If the value is non-zero, changes will occur at a rate equal 10*value 
        milliseconds per step.
        If the value is -1, the function will simply return the current speed.

        Args:
            servo(int): The servo to change.
            |1 <= servo <= 4|
            speed(int): The speed of the servo.
            |-1 <= speed <= 255|

        Returns:
            int: The speed of the servo.
        """

        if (not 1 <= servo <= 4) or (not -1 <= speed <= 255):
            raise ValueError("Inappropriate value for servo speed.")
        
        if speed > -1:
            self.bus.write_byte_data(self.addr, self.servo_registers[servo], speed)
        return self.bus.read_byte_data(self.addr, self.servo_registers[servo])

    def set_servo_target(self, servo, target):
        """Changes the servo position
        Allow the servo pulses to be varied from 0.75mS – 2.25mS with the byte 
        value ranging from 0 – 250.
        If the value is -1, the function will simply return the current target.

        Args:
            servo(int): The servo to change.
            |1 <= servo <= 4|
            speed(int): The speed of the servo.
            |-1 <= speed <= 250|
        
        Returns:
            int: The position of the servo.
        """

        if (not 1 <= servo <= 4) or (not -1 <= target <= 250):
            raise ValueError("Inappropriate value for servo target.")
        
        if target > -1:
            self.bus.write_byte_data(self.addr, self.servo_registers[servo] + 1, target)
        return self.bus.read_byte_data(self.addr, self.servo_registers[servo] + 1)

if __name__ == '__main__':
    """Testing"""
    matrix = Controller(1, 0x08)
    print(matrix.get_info())
    print(matrix.get_status())
    print(matrix.set_timeout(20))
    print(matrix.set_servos([1, 1, 0, -1]))
    print(matrix.set_servo_speed(1, 0))
    print(matrix.set_servo_target(1, 250))