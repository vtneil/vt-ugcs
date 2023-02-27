from deps import *

if __name__ == '__main__':
    parse = StringParser(['x', 'y', 'z', 'w'], ',', None, None)
    d = parse.parse('1,3.5,5,')
    print(d)
    print(parse.unparse(d))
