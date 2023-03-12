from deps import *


if __name__ == '__main__':
    port = SerialPort()
    a = SerialReader(port)

    print(port.is_connected())
