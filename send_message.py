# For the recent testing all the messages sent are the same voice message

import ADPCM_encoder as ad
from digi.xbee.devices import *
import sys
import time

# Find the number of 100 bytes packets and print it
def send_message(isSource, device, remote_device, destination, dup, codec, initial_loss):

	if isSource:
		send_list = ad.run_encoder('first.wav', 2)
		total_number = len(send_list)
		packet_loss = 0

	else:
		total_number = round((1-initial_loss) * len(send_list))
		packet_loss = round(initial_loss *  total_number)

	# this message is required at the realy side for processing
	while True:
		try:
			device.send_data(remote_device, destination)
			break
		except (TimeoutException, XBeeException) as e:
			time.sleep(0.1)

	dup_ratio = 0
	i = 0
	prev = 0 

	for send in send_list:
		try:
			device.send_data(remote_device, send)
			i += 1

		# Keep resending the packet till the duplication ratio is less.
		# The data is repeated just once.
		except (TimeoutException, XBeeException) as e:
			print("Dropped packet number %s" %i)	
			time.sleep(0.08)

			if prev != i:
				prev = i
				dup_ratio += 1
				if (dup_ratio/total_number ) <= dup:
					continue
				else:
					packet_loss += 1
			else:
				packet_loss += 1

	# this message is required at the realy side for processing
	final_list = str(dup_ratio/total_number) + " "+ str(packet_loss/total_number)+ " "+ str(codec)+"f"
	
	while True:
		try:
			device.send_data(remote_device, final_list)
			break
		except (TimeoutException, XBeeException) as e:
			time.sleep(0.1)

def receive_message(received_list, codec):
	original_file = ad.run_decoder(send_list, codec)
	print(original_file)



if __name__ == '__main__':
	main()
