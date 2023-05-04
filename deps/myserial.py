from .base.__HardwareCommunication import SerialReader
from .base.__HardwarePort import SerialPort

ALL_BAUD = (115200, 9600, 110, 300, 600, 1200, 2400, 4800,
            14400, 19200, 38400, 57600, 128000, 256000)

ALL_BAUD_STR = tuple(str(e) for e in ALL_BAUD)
