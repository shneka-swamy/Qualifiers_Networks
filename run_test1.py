import routing_check as rc
import time
import send_message as sm
from digi.xbee.devices import *

def send_message_1(device, remote_device, destination):
	for i in range(1,6):
		sm.send_message(True, device, remote_device, destination, 0, 2, 0, [])
		time.sleep(45)

def send_message_2():
	for i in range(1,6):
		sm.send_message(True, device, remote_device, destination, 0, 2, 0, [])
		time.sleep(55)

def main():
	send_message_1()

if __name__ == '__main__':
	main()
