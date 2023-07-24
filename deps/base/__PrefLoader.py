import json
# import tomllib as toml


class PreferencesLoaderBase:
    @staticmethod
    def load(filename: str):
        raise NotImplementedError

    @staticmethod
    def write(pref_to_write: dict, inp_file_dir: str):
        raise NotImplementedError


class PreferencesLoaderJSON(PreferencesLoaderBase):
    @staticmethod
    def load(filename: str):
        with open(filename, mode='r', encoding='utf-8') as __f:
            return json.load(__f)

    @staticmethod
    def write(pref_to_write: dict, inp_file_dir: str):
        if pref_to_write:
            with open(inp_file_dir, mode='w', encoding='utf-8') as __f:
                json.dump(pref_to_write, __f, indent=4)
            return True
        return False


# class PreferencesLoaderTOML(PreferencesLoaderBase):
#     @staticmethod
#     def load(filename: str):
#         with open(filename, mode='rb') as __f:
#             return toml.load(__f)
#
#     @staticmethod
#     def write(pref_to_write: dict, inp_file_dir: str):
#         pass
