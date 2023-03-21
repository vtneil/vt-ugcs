import time
from deps import *


class ProgramCLI(Program):
    def __init__(self):
        self.settings = PreferencesTree.from_file('settings.json')
        self.data_format = PreferencesTree.from_file('data_format.json')
        self.header = self.settings['header']
        self.file_name = self.settings['file_name']
        self.extension = self.settings['file_extension']
        self.key_lat = self.settings['lat_key']
        self.key_lon = self.settings['lon_key']
        self.key_alt = self.settings['alt_key']

        self.parser = StringParser(self.data_format['0'], header='DEV0,')
        self.writer = FileWriter(__file__, self.file_name, self.extension)
        self.writer_thread: ThreadFileWriter | None = None

        self.port = SerialPort()
        self.port_name = ''
        self.baud = 115200
        self.serial_reader = SerialReader(self.port)
        self.serial_thread: ThreadSerial | None = None

        self.queue = Queue()
        self.queue_csv = Queue()
        self.queue_coord = Queue()

        self.data = Data(self.data_format['0'])

    def start(self):
        self.__prompt_user()
        self.port.connect(self.port_name, self.baud)
        self.serial_thread = ThreadSerial(self.serial_reader, self.parser, self.queue)
        self.serial_thread.start()

        self.writer_thread = ThreadFileWriter(self.writer, self.queue_csv, self.queue_coord)
        self.writer_thread.start()

        self.__prog()

    def stop(self):
        self.serial_thread.stop()
        self.writer_thread.stop()
        self.port.disconnect()

    def __prog(self):
        try:
            while True:
                if self.queue.available():
                    dat_dict: dict = self.queue.pop()
                    dat = list(dat_dict.values())

                    self.data.push(dat)
                    self.queue_csv.push(dat)
                    self.queue_coord.push(
                        GeoCoordinate(dat_dict[self.key_lat], dat_dict[self.key_lon], dat_dict[self.key_alt])
                    )

                    print(self.data.back())

                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def __prompt_user(self):
        while True:
            self.port.refresh()
            all_ports = [(i, k) for i, k in enumerate(self.port.port_pair.keys(), start=1)]
            print('----- Serial Devices -----')
            for i, k in all_ports:
                print('[{}]\t{}'.format(i, k))
            ui = input('Enter a number or type \'r\' to refresh\n').strip()
            if ui.isdigit() and 0 < int(ui) < len(all_ports) + 1:
                self.port_name = self.port.port_pair[all_ports[int(ui) - 1][-1]]
                break
        while True:
            bu = input('Enter baud rate [Leave empty if 115200]\n').strip()
            if bu == '':
                break
            elif bu in ALL_BAUD_STR:
                self.baud = int(bu)
                break


def main():
    program = ProgramCLI()
    program.start()
    program.stop()


if __name__ == '__main__':
    main()
