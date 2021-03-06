from digi.xbee.devices import *
import time
from threading import Event
import send_message as sm
import Quality_check as qc
import run_test1 as rt

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
		self.no_dest = 0
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

		for value in self.table:
			print(value[5], value[4])
			if(value[5] == dest):
				return value[4]
		return 0
 
	def generateRREQ(self, device, dest):
		
		degree = self.neighbourcount
		self.Id += 1
		self.no_dest = len(dest)

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
		self.rrep += self.myAddress

		device.send_data(remote_device, self.rrep)

	def send_message(self, device, remote_device, destination):
		sm.send_message(True, device, remote_device, destination, 0, 2, 0, [])


	def check_inter(self, string_val):
		for list in self.inter_table:
			if list[5] == string_val[5] and list[1] == string_val[1]:
				print("Drop the packet")
				return True
		return False

	# Use a call back function instead ??		
	def sendReply(self, device):

		print("Waiting for data...\n")
		flag = True
		maintain_list = []

		while flag:

			xbee_message = device.read_data()

			if xbee_message is not None:
				string_val = xbee_message.data.decode().split()
				print("Printing received data")
				print(string_val)

				#if string_val[0] == 'PING':
				#	remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (string_val[1]))
				#	device.send_data(remote_device, 'ACCEPT')

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
					quality = qc.QualityCheck(float(quality_list[0]), float(quality_list[1]), int(quality_list[2]))
					print(quality)

					if self.myAddress in address:
						print("received at destination")
						address.remove(self.myAddress)

					if len(address) > 0:
						inter_router = {}
						if quality > 50:
							for addr in address:
								remote = self.	search_table(addr)
								if remote in inter_router:
									temp = inter_router[remote]
									temp.append(addr)
									inter_router[remote] = temp
								else:
									inter_router[remote] = [addr]
						else:
							print("Message dropped - Quality Error")

						if len(inter_router) > 0:
							for inter in inter_router:
								remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (inter))
								sm.send_message(False, device, remote_device, inter_router[inter], float(quality_list[0]), int(quality_list[2]),float(quality_list[1]), new_list)


					

				# Helps identify the Route Request Packet
				# Once a request is got run a timer (must be added later)
				elif string_val[0] == 'RREQ':
						
						flag_inner = False
						#print(self.myAddress in string_val[7:])
						
						if self.myAddress in string_val[7:]:
							if string_val[6] == string_val[5]:
								print("Leaving the packet coming directly from the source")
						
							else:
								if not self.check_inter(string_val):
									self.interTable(string_val)
									remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (string_val[6]))
									self.SeqenceNo += 1
									# Add the source as destianation to the table
									self.updateTable_request(device, string_val)

									print("Generating Reply")
									self.generateRREP(device, remote_device, string_val)
						
						else:
							print("wait")
							print(string_val)
							
							if not self.check_inter(string_val):
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



				elif string_val[0] == 'RREP':

					print("Processing Reply")
					print(string_val)

					if self.myAddress == string_val[4]:
						maintain_list.append(string_val)
						print("Maintain List", maintain_list)

						if len(maintain_list) >= self.no_dest:
							router = {}
					
							for val in maintain_list:
								if val[5] in router:
									temp = router[val[5]]
									print(temp)
									temp.append(val[-1])
									print(temp)
									router[val[5]] = temp 
								else:
									router[val[5]] = [val[-1]]

							print("Router")
							print(router)	

							# Send the message with destination to the routers
							for i in router : 
								print(i) 
								print(router[i])
								remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(i))
								print(str(remote_device))
								# running the test function
								rt.send_message_1(device, remote_device, router[i])
								#self.send_message(device, remote_device, router[i])

					else:
						str_val = string_val.copy()
						self.updateTable_reply(str_val)
						string_val[5] = self.myAddress

						remote_addr = self.search_table(string_val[4])

						if remote_addr == 0:
							print("Wrong Reply Path")
						else:
							print(remote_addr, string_val)
							remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (remote_addr))
							device.send_data(remote_device, ' '.join(string_val))

def main():
	# To open the Xbee device and to work with it

	device = XBeeDevice("/dev/ttyUSB4", 115200)


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



