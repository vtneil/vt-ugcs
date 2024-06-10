from .base.__HardwareCommunication import SerialReader
from .base.__HardwarePort import SerialPort

ALL_BAUD = (460800, 115200, 9600,
            110, 300, 600, 1200, 2400, 4800, 14400, 19200, 38400,
            57600, 76800, 230400, 250000, 500000, 1000000, 2000000)

ALL_BAUD_STR = tuple(str(e) for e in ALL_BAUD)
