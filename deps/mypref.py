from typing import Literal

from .base.__PrefTree import *


class PreferencesTree(PreferencesTreeBase):
    @staticmethod
    def from_file(filename: str, fmt: Literal['json', 'toml'] = 'toml'):
        """
        Open preferences from file

        :param fmt: tree format: toml or json
        :param filename: Preferences file name to open from
        :return: Preferences Tree Object
        """
        if fmt == 'json':
            return PreferencesTree(filename=filename, loader=PreferencesLoaderJSON)
        else:
            return PreferencesTree(filename=filename, loader=PreferencesLoaderTOML)

    @staticmethod
    def from_dict(pref_dict: dict):
        """
        Open preferences from dictionary object

        :param pref_dict: Preferences dictionary
        :return: Preferences Tree Object
        """
        return PreferencesTree(pref_dict=pref_dict)
