import pandas
import pandas as pd
import numpy as np
from collections.abc import Iterable
from collections import deque


class Queue:
    def __init__(self):
        """
        A deque wrapper for ease of use.
        It is thread-safe according to Python docs.

        The queue is simply a "buffer"

        """
        self.__queue = deque()

    def push(self, item):
        self.__queue.append(item)

    def pop(self):
        if self.__queue.__len__() == 0:
            return None
        return self.__queue.popleft()

    def front(self):
        if self.__queue.__len__() == 0:
            return None
        return self.__queue.__getitem__(0)

    def back(self):
        if self.__queue.__len__() == 0:
            return None
        return self.__queue.__getitem__(-1)

    def available(self):
        return self.__len__() > 0

    def __len__(self):
        return self.__queue.__len__()

    def __str__(self):
        return self.__queue.__str__()

    def __repr__(self):
        return self.__queue.__repr__()

    def __getitem__(self, index):
        return self.__queue.__getitem__(index)

    @property
    def data(self):
        return self.__queue


class Data:
    def __init__(self, data_or_header: dict | pd.DataFrame | Iterable = None):
        """
        A wrapper class around Pandas DataFrame for ease of usages.
        Still, you can manipulate the DataFrame data directly.

        :param data_or_header:
        """
        if isinstance(data_or_header, dict) or isinstance(data_or_header, pd.DataFrame):
            # is data
            try:
                self.__data = pd.DataFrame(data_or_header)
            except ValueError:
                self.__data = pd.DataFrame()
        else:
            # is header
            self.__data = pd.DataFrame({k: [] for k in data_or_header})

        self.__headers = self.__data.columns.values.tolist()
        self.__dim = self.__headers.__len__()

    def back(self) -> pd.Series:
        return self.__data.iloc[-1]

    def push(self, data: list | tuple | np.ndarray):
        self.__iadd__(data)

    def pop(self, n: int = -1):
        self.__data.drop(self.__data.index[n], inplace=True)
        self.__data.reset_index(drop=True, inplace=True)

    def pop_many(self, n: int):
        if n < 1:
            return
        n = min(n, self.__len__())
        for i in range(n):
            self.__data.drop(self.__data.index[-1], inplace=True)
        self.__data.reset_index(drop=True, inplace=True)

    def available(self):
        return self.__len__() > 0

    def __getitem__(self, item):
        return self.__data.__getitem__(item)

    def __iadd__(self, other: list | tuple | np.ndarray):
        if other.__len__() == self.__dim:
            self.__data.loc[self.__len__()] = other
            return self

    def __add__(self, other: list | tuple | np.ndarray):
        __data = Data(self.__data)
        __data.__iadd__(other)
        return __data

    def __len__(self):
        return self.__data.__len__()

    def __str__(self):
        return self.__data.__str__()

    def __repr__(self):
        return self.__data.__repr__()

    @property
    def data(self):
        return self.__data

    @property
    def headers(self):
        return self.__headers

    @property
    def dim(self):
        return self.__dim

    @property
    def size(self):
        """
        DataFrame Row x Column

        :return:
        """
        return self.__len__(), self.__dim

    @data.setter
    def data(self, value: pd.DataFrame):
        self.__data = value

    @staticmethod
    def from_df(data: pandas.DataFrame):
        return Data(data)

    def __copy__(self):
        return Data(self.__data)

    def copy(self):
        return self.__copy__()


if __name__ == '__main__':
    dat = Data({'aa': [1, 2, 3, 9],
                'bb': [4, 5, 6, 9],
                'cc': [7, 8, 9, 9]
                })

    d2 = dat.copy()

    dat.pop()

    print(d2)
