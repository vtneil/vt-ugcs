import time
from deps import *
import threading

if __name__ == '__main__':
    x = False

    def m():
        while x:
            time.sleep(0.5)
            print("Hi 1 s")
            time.sleep(0.5)

    t = threading.Thread(target=m, daemon=True)
    x = True
    t.start()
    print("start")
    # x = False
    t.join()
    t = None
    print("end")
