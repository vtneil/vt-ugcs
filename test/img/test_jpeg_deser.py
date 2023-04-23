import serial
from time import sleep

# PORT1_NAME = 'COM3'
PORT2_NAME = '/dev/cu.usbserial-1220'
BAUD_RATE = 115200

FILENAME = 'img'

JPEG_BEGIN = b'\xff\xd8'
JPEG_END = b'\xff\xd9'

# ser1 = serial.Serial(PORT1_NAME, BAUD_RATE)
ser2 = serial.Serial(PORT2_NAME, BAUD_RATE)

if __name__ == '__main__':
    print(ser2)

    with open(f'images/{FILENAME}_-1.jpg', mode='wb') as f:
        f.write(b'')

    try:
        stream = b''
        img_buf = b''
        idx = 1
        bytes_idx = 0

        while True:
            # BEGIN DATA SAVE

            # END DATA SAVE

            # BEGIN IMAGE SAVE
            if ser2.in_waiting > 0:
                new_buf = ser2.read(ser2.in_waiting)
                stream += new_buf

                start = stream.find(JPEG_BEGIN)
                stop = stream.find(JPEG_END)

                print(f'{start = }, {stop = }')
                print(f'Last {len(new_buf)} bytes: ', new_buf, end='\n')

                if start > stop:
                    stream = stream[stream.rfind(JPEG_BEGIN):]
                    print('Invalid start/stop, recapturing...')

                elif -1 < start < stop:
                    img_buf = stream[start:stop + len(JPEG_END)]
                    with open(f'images/{FILENAME}_{idx}.jpg', mode='wb') as f:
                        f.write(img_buf)
                    print('\nImage', idx, 'is saved.')
                    idx += 1
                    stream = b''
                # END IMAGE SAVE

            sleep(0.1)

    except KeyboardInterrupt:
        pass

    # ser1.close()
    ser2.close()
