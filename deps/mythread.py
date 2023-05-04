import time
from .base.__ThreadBase import ThreadBase
from .base.__Parser import ParserBase
from .base.__HardwareCommunication import SerialReader
from .myfile import FileWriter
from .mydata import Queue
from .mylogger import Logger


class ThreadSerial(ThreadBase):
    def __init__(self, reader: SerialReader,
                 parser: ParserBase,
                 queue: Queue,
                 interval: float = 0.050,
                 timeout: float = 4.000):
        """
        Specialized Serial Thread

        :param reader: SerialReader object
        :param parser: String or Bytes Parser object
        :param queue: A multithread Queue object
        :param interval: Serial Buffer polling interval in s, default is 50 ms
        """

        super().__init__(timeout)
        self.__reader = reader
        self.__parser = parser
        self.__queue = queue
        self.__interval = interval
        self.__logger = Logger(target='THREAD_SERIAL')

    def _task(self):
        while self._on:
            self.__reader.read()
            if self.__reader.available():
                msg = self.__reader.get_message()
                if len(msg) > 0:
                    parsed_msg = self.__parser.parse(msg)
                    self.__queue.push(parsed_msg)

            time.sleep(self.__interval)

        # Clear remaining data from the queue
        self.__reader.read()
        while self.__reader.available():
            msg = self.__reader.get_message()
            if len(msg) > 0:
                parsed_msg = self.__parser.parse(msg)
                self.__queue.push(parsed_msg)

    @property
    def queue(self):
        return self.__queue

    @property
    def _logger(self):
        return self.__logger


class ThreadFileWriter(ThreadBase):
    def __init__(self, file_writer: FileWriter,
                 queue_csv: Queue,
                 queue_coord: Queue,
                 queue_raw: Queue = None,
                 interval: float = 0.050,
                 timeout: float = 4.000):
        """
        Specialized Thread for writing files in the background without blocking main thread.

        :param file_writer: FileWriter object
        :param queue_csv: Queue for data list
        :param queue_coord: Queue for coordinates
        :param interval: Serial Buffer polling interval in s, default is 50 ms
        """

        super().__init__(timeout)
        self.__writer = file_writer
        self.__queue_csv = queue_csv
        self.__queue_coord = queue_coord
        self.__queue_raw = queue_raw if queue_raw is not None else Queue()
        self.__interval = interval
        self.__logger = Logger(target='THREAD_FILE')

    def _task(self):
        while self._on:
            if self.__queue_csv.available():
                dat = self.__queue_csv.pop()
                self.__writer.append_csv(dat)

            if self.__queue_coord.available():
                dat = self.__queue_coord.pop()
                self.__writer.append_coord(dat)

            if self.__queue_raw.available():
                dat = self.__queue_raw.pop()
                self.__writer.append_csv(dat)

            time.sleep(self.__interval)

        # Clear remaining data from the queue
        while self.__queue_csv.available():
            dat = self.__queue_csv.pop()
            self.__writer.append_csv(dat)

        while self.__queue_coord.available():
            dat = self.__queue_coord.pop()
            self.__writer.append_coord(dat)

    @property
    def queue_csv(self):
        return self.__queue_csv

    @property
    def queue_coord(self):
        return self.__queue_coord

    @property
    def queue_raw(self):
        return self.__queue_raw

    @property
    def _logger(self):
        return self.__logger
