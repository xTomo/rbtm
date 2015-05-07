from shutter import Shutter

from time import sleep
if __name__ == "__main__":
    s = Shutter('COM7', 4)
    s.open()
    print(s.is_open())
    sleep(0.5)
    s.close()
    print(s.is_open())
