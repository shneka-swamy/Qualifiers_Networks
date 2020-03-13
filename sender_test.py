from digi.xbee.devices import *
import time


def main():

    device = XBeeDevice("/dev/ttyUSB2", 250000)

    try:
        device.open()

        remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string
                                ("0013A200419B580F"))

        while(True):
            print("Enter a message: ")
            message = input()
            print("Repetitions: ")
            reps = int(input())
            start_time = time.time()
            i = 0
            failed_transmissions = 0
            while(i < reps):
                try:
                    device.send_data(remote_device, message)
                    i+=1
                except (TimeoutException, XBeeException) as e:
                    print("Dropped packet number %s" %i)
                    time.sleep(0.1)
                    failed_transmissions+=1
                    continue

                    
            print("Success")
            print("Elapsed time: %s" %(time.time() - start_time))
            print("Drop rate: %s" %(failed_transmissions / reps))

    except InvalidOperatingModeException:
        print("Invalid mode error: Restart module")
    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == "__main__":
    main()