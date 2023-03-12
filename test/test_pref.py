from deps import *


if __name__ == '__main__':
    pref = PreferencesTree.from_file('../settings.json')
    print(pref.tree)
