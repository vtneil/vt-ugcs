from .base.__Parser import *
from .base.__CustomException import ConstructorException


class StringParser(ParserBase):
    def __init__(self,
                 data_format: list[str] | Iterable[str] | Sized,
                 delimiter: str = ',',
                 header: str = None,
                 tail: str = None,
                 *args, **kwargs):
        """
        Parse string with delimiter, header (if any), and tail (if any).

        The header and tail is searched and will be cut.

        None type is defined as missing values in fields

        :param data_format: Data format, iterable, sized
        :param delimiter: Delimiter of string (default: comma)
        :param header: Header of string (if any)
        :param tail: Tail of string (if any)
        :param args:
        :param kwargs:
        """
        super().__init__(data_format, args, kwargs)
        self.__header = header or None
        self.__delimiter = delimiter or ','
        self.__tail = tail or None

        if self.__delimiter is None:
            raise ConstructorException('Delimiter cannot be None')
        if self.__tail is not None and self.__header is None:
            raise ConstructorException('Header is None but Tail is not None!')

    def parse(self, data: str) -> dict:
        """
        Parse the data according to the preset.

        **Note that the behavior of having trailing delimiter is defined as missing value.**

        :param data:
        :return:
        """
        if self.__header is None:
            return self.__parse_delim_only(data)
        if self.__tail is None:
            return self.__parse_with_header(data)
        return self.__parse_with_tail(data)

    def unparse(self, data: dict):
        """
        Unparse dictionary data into preset string

        :param data:
        :return:
        """
        __data_dict = self.make_blank()
        __data_dict.update(data)
        __payload = self.__delimiter.join([str(v) if v is not None else '' for v in __data_dict.values()])
        if self.__header is None:
            return __payload
        if self.__tail is None:
            return self.__header + __payload
        return self.__header + __payload + self.__tail

    def __parse_delim_only(self, __data: str):
        __data_list = __data.split(self.__delimiter)
        __data_dict = self.make_blank()
        for k, v in zip(__data_dict.keys(), __data_list):
            __data_dict[k] = self.final_type(v)
        return __data_dict

    def __parse_with_header(self, __data: str):
        if __data.find(self.__header) != 0:
            return self.make_blank()
        return self.__parse_delim_only(__data[len(self.__header):])

    def __parse_with_tail(self, __data: str):
        if __data.rfind(self.__tail) != len(__data) - len(self.__tail):
            return self.make_blank()
        return self.__parse_with_header(__data[:-len(self.__tail)])


class BytesParser(ParserBase):
    def parse(self, *args, **kwargs) -> dict:
        pass

    def unparse(self, *args, **kwargs):
        pass
