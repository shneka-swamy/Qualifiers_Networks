from digi.xbee.devices import *
import time
from threading import Event
import send_message as sm
import Quality_check as qc

# Edit the code for multiple destiantions (can be implemented later)


class RouteFormation:

	# The route request uses the following message pattern to set up communication
	# Source Request is <Broadcast ID, Sequence Number , Hop Number, Degree, Source ID, Intermediate ID , Destination ID (number can vary)>
	# Route Reply is of the form <Sequence Number, Hop Number, Degree, Source, Intermediate, Destination >
	def __init__(self, device):
		self.rreq = ""
		self.isSource = False
		self.SeqenceNo = 0
		self.Id = 0
		self.destination = []
		self.table = []
		self.inter_table = []
		self.rem = []
		self.neighbourcount = 0
		self.rrep = ""
		self.myAddress = str(device.get_64bit_addr())

	# <Sequence Number, Hop number, Degree, Source ID, Intermediate ID, Destination ID, Expiry Time>
	def createTable(self, device):
		print("Entered")
		self.device_discovery(device)
		self.neighbourcount = len(self.rem)
			
		if self.neighbourcount == 0:
			print("No neighbour found so far try after sometime")
		else:
			for i in range(0, self.neighbourcount):
				self.table.append([str(self.SeqenceNo), str(1), str(self.neighbourcount),self.myAddress,self.rem[i],self.rem[i], 5])
		
		#print(self.table) 

	# <Sequence Number,Hop Number, Degree, Source ID, Intermediate ID, Destiantion ID, Expiry>
	def updateTable_reply(self, message):
		
		for block in self.table:
			
			# Don't make any changes if the time for keeping the block expires
			if block[-1] == 0:
				self.table.remove(block)
			# If the destination is the same 
			# This happens when the sequence number is greater or the hop number is lower
			else:
				if message[6] == block[5] and (int(block[0]) < int(message[1]) and int(block[1])  > int(message[2])):
					block[:] = message[1:7] 
					block.append(5)
		#print("Table Updated at Reply:")
		#print(self.table)

	# Must check the logic behind this part 
	def updateTable_request(self, device, message):
		for block in self.table:
			
			if block[-1] == 0:
				self.table.remove(block)
			# If the destiantion needs to be chaged
			# This happens when the sequence number is greater or the block number is lower
			else:
				if message[5] == block[5] and (int(block[0]) <  int(message[2]) or int(block[1]) > int(message[3])):
					print("Actually updating table")
					block[:] = message[2:5]
					block.append(self.myAddress)
					block.append(message[6])
					block.append(message[5])
					block.append(5)

		#print("Table Updated at Request:")
		#print(self.table)


	def search_table(self, dest):
		print(self.table)
		print("Checking the values")
		print(dest)

		# Generate a list of list with the destination and the intermediate node
		final_list = []

		for value in self.table:
			print(value[5]

			for destination in dest:
				if(value[5] == destination):
					final_list.append([destination, value[4]])
		return final_list
 
	def generateRREQ(self, device, dest):
		
		degree = self.neighbourcount
		self.Id += 1

		self.rreq += str('RREQ ') + str(self.Id) + ' ' + str(self.SeqenceNo) + ' ' + str(1) + ' ' + str(degree) + ' '
		self.rreq += self.myAddress + ' ' + self.myAddress+ ' '
		self.rreq += ' '.join(dest)
		print("<Sequence Number, Broadcast ID, Hop Number, Degree, Source ID, InterSource, Destintion ID>")
		print(self.rreq)
		
		# Drop the packet when duplicated and when multiple path request are made at the same time.
		self.interTable(self.rreq.split())
		# Every message sent will increase the sequence number
		self.SeqenceNo += 1
		device.send_data_broadcast(self.rreq)

		self.sendReply(device)
		
	def declareSource(self, device, dest):
		self.isSource = True
		self.generateRREQ(device, dest)


	# Code that discovers other devices in the network 
	# Discovers itself and other devices in range with the same baud rate.
	def device_discovery(self, device):
		xbee_net = device.get_network()
		xbee_net.set_discovery_timeout(15)
		xbee_net.clear()

		def callback_device_discovered(remote):
			print("Device discovered is %s" %remote)
			self.rem.append(str(remote).split()[0])

		def callback_discovery_finished(status):
			if status == NetworkDiscoveryStatus.SUCCESS:
				print("Discovery process finished successfully")
			else:
				print("Discovery process not successful")

		xbee_net.add_device_discovered_callback(callback_device_discovered)
		xbee_net.add_discovery_process_finished_callback(callback_discovery_finished)
		xbee_net.start_discovery_process()

		print("Discovering Remote XBee Devices.")

		while xbee_net.is_discovery_running():
			time.sleep(0.1)

	# This table can be used to get back to the source (must not be dropped)
	# This is same as the information received from the route request
	def interTable(self, message):
		# Consist of the information in the received queue 
		# Essentially requires only braodcast Id and source. (Other details are stored for possible optimisation)
		self.inter_table.append(message)
		print("Intermediate  Table :")
		print(self.inter_table)

    #<Sequence Number, Hop number, degree, Source Id, Intermediate Id, Destination ID>
	def generateRREP(self, device, remote_device,  message):
		#degree = self.neighbourcount
		# Do not change the hop count and the degree when sending back the reply.

		self.rrep += str('RREP ')+ str(self.SeqenceNo) + ' ' + message[3] + ' ' + message[4] + ' '
		self.rrep += message[5] + ' ' + self.myAddress + ' '
		self.rrep += message[7]

		device.send_data(remote_device, self.rrep)

	def send_message(self, device, remote_device, destination):
		sm.send_message(True, device, remote_device, destination, 0, 2, 0, [])

	# Use a call back function instead ??		
	def sendReply(self, device):

		print("Waiting for data...\n")
		flag = True

		while flag:
			xbee_message = device.read_data()

			if xbee_message is not None:
				string_val = xbee_message.data.decode().split()
				print("Printing received data")
				print(string_val)

				if string_val[0] == 'MSG':
					address = string_val[1:]
					print("information is received, Waiting for data:")
					print(address)
					
					# Check if it works for one hop
					final_message = []
					while True:
						message = device.read_data()

						if message is not None:
							msg = message.data.decode().split()
							i = 0

							if len(msg) == 2 and (msg[0] == 'PING' or msg[0] == "CHCK"):
								pass
							elif msg[0] == 'RREQ' or msg[0] == 'RREP':
								pass
							elif len(msg) == 4 and msg[-1] == 'f':
								final_message += msg
								print("Finished Receving data")
								break
							else:
								final_message += msg
								i += 1
								print(i)

					# This is the actual audio data
					new_list = final_message[:-4]

					# Check the quality
					quality_list = final_message[-4:-1]
					
					#To convert to original audio
					sm.receive_message(new_list, int(quality_list[2]))

					my_message = False

					if self.myAddress in address:
						
						print("Message received at the receiver end")
						# This is the actual audio quality data
						print(quality_list)
						qc.QualityCheck(float(quality_list[0]), float(quality_list[1]), int(quality_list[2]))
						address.remove(self.myAddress)
						my_message = True

					# Check in the table and transfer the information 
					final_list = self.search_table(address)
					if len(final_list) == 0 and my_message == False:
						print("Error in path")
					elif len(final_list) == 0 and my_message == True:
						print("I am the only receiver in the path")
					else:
						print(quality_list)
						for common_path in final_list:
							sm.send_message(False, device, common_path[1], common_path[0], float(quality_list[0]), float(quality_list[1]), int(quality_list[2]), new_list)
				

				# Helps identify the Route Request Packet
				# Once a request is got run a timer (must be added later)
				elif string_val[0] == 'RREQ':
						
						flag_inner = False
						print(self.myAddress in string_val[7:])
						if self.myAddress in string_val[7:]:
							if string_val[6] == string_val[5]:
								print("Leaving the packet coming directly from the source")
						
							else:
								# Is the message already in the list
								for list in self.inter_table:
									# Already a path is got. Check the value with the previous path 
									# First preference is given to hop value and then to congestion domain
									if list[5] == string_val[5] and list[1] == string_val[1]:
										change_flag = False
										
										if new_value[7:].count('1') < (string_val[7:].count('1') + 1):
											if int(new_value[3]) >= int(string_val[3] - 1):
												if (int(new_value[4]) > int(string_val[4])) and (int(new_value[2])) < (int(string_val[2])):
													new_value = string_val.copy()
													change_flag = True

										elif int(new_value[3]) >= int(string_val[3] - 1):
											if int(new_value[4]) > int(string_val[4]) and (int(new_value[2])) < (int(string_val[2])) :
													new_value = string_val.copy()
													change_flag = True
										
										if change_flag == True:
											for i in range(7, len(string_val)):
												if (new_value[i] == self.myAddress):
													new_value[i] = str(1)


										flag_inner = True


								if flag_inner == False:
									self.interTable(string_val)
									new_value = string_val.copy()

									for i in range(7, len(string_val)):
										if (new_value[i] == self.myAddress):
											new_value[i] = str(1)

									Event().wait(2)

								remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (new_value[6]))
								self.SeqenceNo += 1
								# Add the source as destianation to the table
								self.updateTable_request(device, new_value)	

								# There are still destinations to be found
								if new_value[7:].count('1') != len(new_value) - 7:
									new_value[6] = self.myAddress
									new_value[4] = str(int(new_value[4]) + (self.neighbourcount-1))
									new_value[3] = str(int(new_value[3]) + 1)

									device.send_data_broadcast(' '.join(new_value))

									self.SeqenceNo += 1

								print("Generating Reply")
								self.SeqenceNo += 1

								new_value[0] = 'RREP '
								for i in range(1,5):
									new_value[i] = new_value[i+1]

								new_value.append(self.myAddress)
								new_value.append(self.myAddress)
								print(new_value)
								self.generateRREP(device, remote_device, new_value)
						
						else:
							print("wait")
							print(string_val)
							drop_flag = False

							for list in self.inter_table:
								if list[5] == string_val[5] and list[1] == string_val[1]:
									print("Drop the package already received")
									drop_flag = True

							if drop_flag == False:
								str_val = string_val.copy()
								self.interTable(str_val)
								self.updateTable_request(device, string_val)
								self.SeqenceNo += 1
							
								string_val[6] = self.myAddress
								string_val[4] = str(int(string_val[4]) + (self.neighbourcount - 1))
								string_val[3] = str(int(string_val[3]) + 1)
								print("Checking the values before sending")
								print(self.inter_table)
								device.send_data_broadcast(' '.join(string_val))

				# When the value of the message received is 6 a reply message is received.
				# Look at the intermediate table and send the message through the intermediate node.
				elif string_val[0] == 'RREP':
					print("Processing Reply:")
					path_flag = True

					print(string_val)
					print("Checking the intermediate table")
					print(self.inter_table)

					for member in self.inter_table:
						print("Check the graph")
						if string_val[6] in member[7:] and member[5] == string_val[4]: 
							self.updateTable_reply(string_val)
							print("Printing intermediate table for verification")
							print(self.inter_table)
							path_flag = False
							break

					if path_flag == True:
						print("Error. Wrong reply received, node not in path")
					
					else:
						maintain_list = []
						if self.myAddress == string_val[4]:

							if len(maintain_list) == 0:
								maintain_list.append(string_val)
								print(maintain_list)
								Event().wait(2)	

							# this considers the case of two nodes talking to one common node
							if maintain_list[0][5] == maintain_list[1][5]:
								remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (maintain_list[0][5]))
								print("Send Data - Path Set")
								# First send the destination address and then send the message.
								self.send_message(device, remote_device, maintain_list[0][6])
							else:
								for maintain in maintain_list:
									remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (maintain[5]))
									print(maintain[5])
									print(maintain[6])
									print("Send Data - Path Set")
									# First send the destination address and then send the message.
									self.send_message(device, remote_device, maintain[6])

							
						else:
							print("Forward not the source")
							# Change the intermediate ID
							string_val[5] = self.myAddress
							remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(member[6]))

							print(self.inter_table)
							print(member)
							print(string_val)

							device.send_data(remote_device,' '.join(string_val))	



def main():


	# To open the Xbee device and to work with it

	device = XBeeDevice("/dev/ttyUSB0", 115200)


	device.open()
	print(device.get_power_level())

	# Create an object for sending Route Request for a message
	# In the beginning of the program - do the following 
	rreq = RouteFormation(device)	
	rreq.createTable(device)

	# This function must be called when not set as a source
	#rreq.sendReply(device)

	# These steps are inherent to source node.
	# print ("Press 'y' to declare as the source")	

	rreq.declareSource(device, ['0013A20040B317F6', '0013A2004102FC76'])
	#rreq.declareSource(device, ['0013A200419B587E'])
	#rreq.declareSource(device, "0013A2004102FC76")
	#rreq.declareSource(device, "0013A20040B31805")


	device.close()

if __name__ == "__main__":
	main()


