from collections.abc import Iterable

import numpy as np


class BaseParser:
    def __init__(self, data_format: Iterable[str], *args, **kwargs):
        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        raise NotImplementedError
