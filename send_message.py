# For the recent testing all the messages sent are the same voice message

import ADPCM_encoder as ad
from digi.xbee.devices import *
import sys
import time

# Find the number of 100 bytes packets and print it
def send_message(isSource, device, remote_device, destination, dup, codec, initial_loss, send_list):

	if isSource:
		send_list = ad.run_encoder('first.wav', codec)
		total_number = len(send_list)
		print(total_number)
		packet_loss = 0

	else: 		
		total_number = round(len(send_list) / (1 - initial_loss))
		packet_loss = round(initial_loss *  total_number)

	# this message is required at the realy side for processing
	while True:
		try:
				msg = "MSG " + destination
				device.send_data(remote_device, msg)
				break
			except (TimeoutException, XBeeException) as e:
				time.sleep(0.1)

	print("Finished First Part")
	dup_ratio = 0
	i = 0
	prev = 0 

	print(len(send_list))

	for send in send_list:
		try:
			print("Sending Packet")
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
				if (dup_ratio/total_number) <= dup:
					continue
				else:
					packet_loss += 1
			else:
				packet_loss += 1

	# this message is required at the realy side for processing
	final_list = str(dup_ratio/total_number) + " "+ str(packet_loss/total_number)+ " "+ str(codec)+" f"
	print ("Doing the last part")

	while True:
		try:
			print(final_list)
			device.send_data(remote_device, final_list)
			break
		except (TimeoutException, XBeeException) as e:
			time.sleep(0.1)

def receive_message(received_list, codec):
	original_file = ad.run_decoder(received_list, codec)


