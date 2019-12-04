from digi.xbee.devices import *
import time


def main():

    device = XBeeDevice("/dev/ttyUSB6", 115200)
    device.open()

    while True:

        i = 0
        while i in range(0, 10):
            print("PING")
            device.send_data_broadcast('PING PING')
            time.sleep(0.1)
            i += 1 

        time.sleep(10)


if __name__ == '__main__':
    main()