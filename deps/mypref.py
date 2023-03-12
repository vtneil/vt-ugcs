from .base.__PrefTree import *


class PreferencesTree(PreferencesTreeBase):
    @staticmethod
    def from_file(filename: str):
        """
        Open preferences from file

        :param filename: Preferences file name to open from
        :return: Preferences Tree Object
        """
        return PreferencesTree(filename=filename)

    @staticmethod
    def from_dict(pref_dict: dict):
        """
        Open preferences from dictionary object

        :param pref_dict: Preferences dictionary
        :return: Preferences Tree Object
        """
        return PreferencesTree(pref_dict=pref_dict)
