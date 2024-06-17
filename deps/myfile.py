import os
import typing
from collections.abc import Iterable
import numpy as np
from .mygis import GeoCoordinate


class _GoogleEarthKMLText:
    class Color:
        WHITE = 'ffffffff'
        RED = 'ff0000ff'
        GREEN = 'ff00ff00'
        BLUE = 'ffff0000'
        YELLOW = 'ff00ffff'
        PURPLE = 'ff800080'
        ORANGE = 'ff0080ff'
        BROWN = 'ff336699'

    colors = [
        Color.YELLOW,
        Color.PURPLE,
        Color.ORANGE,
        Color.BLUE,
        Color.RED,
        Color.GREEN,
        Color.BROWN,
        Color.WHITE
    ]

    earth_live_pre = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                      '<kml xmlns="http://www.opengis.net/kml/2.2" '
                      'xmlns:gx="http://www.google.com/kml/ext/2.2">\n'
                      '<NetworkLink>\n'
                      '<Link>\n<href>')
    earth_live_post = ('</href>\n<refreshMode>onInterval</refreshMode>\n'
                       '<refreshInterval>0.1</refreshInterval>\n'
                       '</Link>\n'
                       '</NetworkLink>\n'
                       '</kml>\n')

    earth_coord_0 = ('<kml xmlns="http://www.opengis.net/kml/2.2" '
                     'xmlns:gx="http://www.google.com/kml/ext/2.2">\n'
                     '<Folder>\n'
                     '<name>Log</name>\n'
                     '<Placemark>\n'
                     '<name>Device Path Plotting</name>\n'
                     '<Style>\n'
                     '<LineStyle>\n<color>')
    earth_coord_1 = ('</color>\n<colorMode>normal</colorMode>\n'
                     '<width>3</width>\n'
                     '</LineStyle>\n'
                     '<PolyStyle>\n'
                     '<color>99000000</color>\n'
                     '<fill>1</fill>\n'
                     '</PolyStyle>\n'
                     '</Style>\n'
                     '<LineString>\n'
                     '<extrude>1</extrude>\n'
                     '<gx:altitudeMode>absolute</gx:altitudeMode>\n'
                     '<coordinates>\n')
    earth_coord_2 = ('\n</coordinates>\n'
                     '</LineString>\n'
                     '</Placemark>\n'
                     '</Folder>\n'
                     '</kml>')


class FileUtil:
    @staticmethod
    def new_filename(filename: str):
        dpos = filename.rfind('.')
        if dpos != -1:
            idx = 0
            while os.path.isfile(fname := f'{filename[:dpos]}_{idx}.{filename[dpos + 1:]}'):
                idx += 1
        else:
            idx = 0
            while os.path.isfile(fname := f'{filename}_{idx}'):
                idx += 1
        return fname

    @staticmethod
    def mkdir(dirname: str):
        """
        Make directory if not exist

        :param dirname: Directory name
        :return:
        """
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    @staticmethod
    def insert_at_line(filename: str, line_no: int, text: str, latest_pos: int = 0):
        """
        This static method inserts a line into mth line (m >= 0) which
        is an optimized alternative of rewriting the whole file.

        :param filename: File name or file path (str)
        :param line_no: Line number, can be absolute (>= 0) or relative to last element (< 0)
        :param text: Object which str() is callable to insert
        :param latest_pos: The latest file pointer position, put the return value of last position
        :return: The latest file position, put it in next argument call
        """
        last_end = []
        _p_file = 0
        with open(filename, "r+", encoding='utf-8') as fro:
            if latest_pos == 0:
                if line_no < 0:
                    _max_line = FileUtil.line_count(fro)
                    _lineno = _max_line + line_no
                else:
                    _lineno = line_no
                fro.seek(0)
                if _lineno < 0:
                    _lineno = 0
                _pos = 0
                _line = fro.readline()
                while _line:
                    if _pos == _lineno - 1:
                        _p_file = fro.tell()
                    if _pos >= _lineno:
                        last_end.append(_line)
                    _line = fro.readline()
                    _pos += 1
                fro.seek(_p_file)
            else:
                fro.seek(latest_pos)
                _line = fro.readline()
                while _line:
                    last_end.append(_line)
                    _line = fro.readline()
                fro.seek(latest_pos)
            fro.write(str(text) + '\n')
            new_latest_pos = fro.tell()
            fro.writelines(last_end)
        return new_latest_pos

    @staticmethod
    def blocks(file_object: typing.IO, size: int = 2 ** 16):
        """
        Lazy block read

        :param file_object: File object
        :param size: Block size
        :return:
        """
        while True:
            b = file_object.read(size)
            if not b:
                break
            yield b

    @staticmethod
    def line_count(file_object: typing.IO):
        """
        Lazy line counting

        :param file_object: File object
        :return: Number of lines in the file
        """
        return sum(bl.count('\n') for bl in FileUtil.blocks(file_object))


class FileWriter:
    ref_cnt = 0

    def __init__(self, root_file: str,
                 save_name: str,
                 extension: str = 'csv', /, *,
                 device_id: int | str = 0,
                 folder_name: str = 'data'):
        """
        File logger for writing delimited data file and Google Earth KML file

        :param root_file: Manually type "__file__" here
        :param save_name: Name of the file
        :param extension: Extension of the delimited file, default is "csv"
        :param device_id: Device id, default is 0
        :param folder_name: Folder name, default is "data"
        """
        # Arguments saving
        self.root_file = root_file
        self.root_path = self.__root_path
        self.device_id = str(device_id)
        self.save_name = save_name
        self.extension = extension.strip('.')
        self.folder_name = folder_name

        # File postfix naming
        self.__dev = '_dev{}'.format(self.device_id)
        self.__postfix = '_{}{}'.format(self.save_name, self.__dev)

        # Dynamically generated Files
        self.name_kml_save = FileUtil.new_filename(
            self.data_path('coord_save{}.kml'.format(self.__postfix))
        )
        self.name_csv_save = FileUtil.new_filename(
            self.data_path('data{}.{}'.format(self.__postfix, self.extension))
        )
        self.name_raw_save = FileUtil.new_filename(
            self.data_path('data{}.raw'.format(self.__postfix))
        )

        # Google Earth KML Reference File
        self.name_kml_ref = self.data_path(
            'coord_ref{}.kml'.format(self.__dev)
        )
        self.name_kml_live = self.data_path(
            'coord_live{}.kml'.format(self.__dev)
        )

        # Initialize file pointer (cursor)
        self.__ptr_save, self.__ptr_ref = 0, 0

        # Pair KML files
        self.__kml_pair = (self.name_kml_save, self.name_kml_ref)

        # Initialize directory
        FileUtil.mkdir(self.folder_name)
        self.__renew_kml()

        self.id = FileWriter.ref_cnt % len(_GoogleEarthKMLText.colors)

        FileWriter.ref_cnt += 1

    def append_csv(self, data: np.ndarray | list | tuple | Iterable, delimiter: str = ','):
        """
        Append list or numpy array of data to the file in delimited format

        :param data: Data in list or numpy array
        :param delimiter: Delimiter, default is comma ","
        :return:
        """
        if len(data) < 1:
            return
        with open(self.name_csv_save, mode='a', encoding='utf-8') as f:
            f.write(delimiter.join(str(e) for e in data))
            f.write('\n')

    def append_coord(self, coord: GeoCoordinate):
        """
        Append coordinate to Google Earth KML reference file, this method does not create
        live KML file. User must call another method to create it.

        :param coord: GeoCoordinate object
        :return:
        """
        if not coord.valid():
            return
        __lat, __lon, __alt = (
            '{:.6f}'.format(coord.lat),
            '{:.6f}'.format(coord.lon),
            '{:.2f}'.format(coord.alt)
        )

        __coord = '{},{},{}'.format(__lon, __lat, __alt)

        color = _GoogleEarthKMLText.colors[self.id]

        self.__ptr_ref = self.__append_kml(__coord, self.name_kml_ref, self.__ptr_ref, color)
        self.__ptr_save = self.__append_kml(__coord, self.name_kml_save, self.__ptr_save, color)

    @staticmethod
    def __append_kml(__coord, __filename, __file_ptr, __color):
        if __file_ptr == 0:
            with open(__filename, mode='w', encoding='utf-8') as f:
                f.write(_GoogleEarthKMLText.earth_coord_0)
                f.write(__color)
                f.write(_GoogleEarthKMLText.earth_coord_1)
                f.write(__coord)
                f.write(_GoogleEarthKMLText.earth_coord_2)

        __file_ptr_new = FileUtil.insert_at_line(__filename, -5, __coord, __file_ptr)
        return __file_ptr_new

    @property
    def __root_path(self):
        return os.path.abspath(os.path.dirname(self.root_file))

    def __renew_kml(self):
        if os.path.isfile(self.name_kml_ref):
            os.remove(self.name_kml_ref)
        if os.path.isfile(self.name_kml_live):
            return
        with open(self.name_kml_live, mode='w', encoding='utf-8') as f:
            f.write(_GoogleEarthKMLText.earth_live_pre)
            f.write(self.name_kml_ref)
            f.write(_GoogleEarthKMLText.earth_live_post)

    def data_path(self, filename: str = None):
        """
        Returns absolute path of data folder or filename in data folder

        :param filename: File name
        :return: Absolute path
        """
        __path = os.path.join(self.root_path, self.folder_name)
        if filename is not None:
            __path = os.path.join(self.root_path, self.folder_name, filename)
        return str(__path)
