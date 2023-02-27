import json
from .__exception import ArgumentException


class BasePreferencesTree:
    def __init__(self, filename: str = None, pref_dict: dict = None):
        self.__pref = None
        self.__filename = 'settings.json'

        if filename is not None and pref_dict is not None:
            raise ArgumentException('Wrong argument called on BasePreferencesTree!')
        if filename is None and pref_dict is None:
            raise ArgumentException('No argument called on BasePreferencesTree!')
        if filename is not None:
            self.__filename = filename
            with open(filename, mode='r', encoding='utf-8') as __f:
                self.__pref = json.load(__f)
        elif pref_dict is not None:
            self.__pref = pref_dict

    @property
    def tree(self):
        return self.__pref

    def __getitem__(self, item: str):
        return self.__pref[item]

    def __setitem__(self, key, value):
        self.__pref[key] = value
        return

    def setdefault(self, key, value):
        self.__pref.setdefault(key, value)

    def remove(self, key):
        """
        Remove value from preferences tree

        :param key: Key
        :return: Value removed
        """
        return self.__pref.pop(key)

    def __len__(self):
        return self.__pref.__len__()

    def save(self, filename: str = None):
        """
        Save preferences tree to json file

        :param filename: File name to save to
        :return:
        """
        if filename is None:
            self.write_json(self.__pref, self.__filename)
        else:
            self.write_json(self.__pref, filename)
        return

    @staticmethod
    def write_json(pref_to_write: dict, inp_file_dir: str, *, indent: int = 4):
        """
        Write dictionary to json file

        :param pref_to_write: Dictionary
        :param inp_file_dir: File name
        :param indent: Indentation space
        :return:
        """
        if pref_to_write:
            with open(inp_file_dir, mode='w', encoding='utf-8') as __f:
                json.dump(pref_to_write, __f, indent=indent)
            return True
        return False
