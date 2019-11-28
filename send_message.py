# For the recent testing all the messages sent are the same voice message

import ADPCM_encoder as ad
from digi.xbee.devices import *
import sys


# Find the number of 100 bytes packets and print it
def send_message(isSource, device, remote_device, destination):

	if isSource:
		send_list = ad.run_encoder('first.wav', 2)

	# Append the codec to the destinations side 
	# enables decoding at the other end
	device.send_data(remote_device, destination)

	for send in send_list:
		device.send_data(remote_device, send)


def receive_message(received_list, codec):
	original_file = ad.run_decoder(send_list, codec)
	print(original_file)



if __name__ == '__main__':
	main()
