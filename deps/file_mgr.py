import os
import typing
import numpy as np


class FileUtil:
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
