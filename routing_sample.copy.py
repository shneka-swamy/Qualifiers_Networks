from digi.xbee.devices import *
import time
from threading import Event
import send_message as sm
import Quality_check as qc


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

	def createTable(self, device):
		print("Entered")

		self.device_discovery(device)
		self.neighbourcount = len(self.rem)
			
		if self.neighbourcount == 0:
			print("No neighbour found so far try after sometime")
		else:
			for i in range(0, self.neighbourcount):
				self.table.append([str(self.SeqenceNo), str(1), str(self.neighbourcount),self.myAddress,self.rem[i],self.rem[i], 5])
		
		print(self.table) 

	
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

	def interTable(self, message):
		self.inter_table.append(message)
		print("Intermediate  Table :")
		print(self.inter_table)


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
		
		# self.sendReply(device)

	def declareSource(self, device, dest):
		self.isSource = True
		self.generateRREQ(device, dest)


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

	def sendReply(self, device):

		print("Waiting for data...\n")
		flag = True

		while flag:
			xbee_message = device.read_data()

			if xbee_message is not None:
				string_val = xbee_message.data.decode().split()
				print("Printing received data")
				print(string_val)

				if string_val[0] == 'RREQ':
						
						flag_inner = False
						
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
											if int(new_value[3]) >= int(string_val[3]) - 1:
												if (int(new_value[4]) > int(string_val[4])) and (int(new_value[2])) < (int(string_val[2])):
													new_value = string_val.copy()
													change_flag = True

										elif int(new_value[3]) >= int(string_val[3] - 1):
											if int(new_value[4]) > int(string_val[4]) and (int(new_value[2])) < (int(string_val[2])) :
													new_value = string_val.copy()
													change_flag = True

										else:
											print("Better option available")
										
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
											break


								print('Visited')
								remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string (new_value[6]))
								self.SeqenceNo += 1
								# Add the source as destianation to the table
								self.updateTable_request(device, new_value)	

								# There are still destinations to be found
								if new_value[7:].count('1') != len(new_value) - 7:
									
									send_value = new_value.copy()

									send_value[6] = self.myAddress
									send_value[4] = str(int(new_value[4]) + (self.neighbourcount-1))
									send_value[3] = str(int(new_value[3]) + 1)

									device.send_data_broadcast(' '.join(new_value))

									self.SeqenceNo += 1

								print("Generating Reply")
								self.SeqenceNo += 1

								reply_value = new_value.copy()

								reply_value[0] = 'RREP'
								for i in range(1,5):
									reply_value[i] = new_value[i+1]

								reply_value = reply_value[0:5]
								reply_value.append(self.myAddress)
								reply_value.append(self.myAddress)
								print("Printing Reply")
								print(reply_value)

								#Event().wait(10)

								device.send_data(remote_device, ' '.join(reply_value))

								#self.generateRREP(device, remote_device, new_value)
						
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


				



def main():


	# To open the Xbee device and to work with it

	device = XBeeDevice("/dev/ttyUSB3", 115200)


	device.open()
	print(device.get_power_level())
	rreq = RouteFormation(device)	
	rreq.createTable(device)

	rreq.sendReply(device)

	#rreq.declareSource(device, ['0013A20040B317F6', '0013A2004102FC76'])

	device.close()

if __name__ == "__main__":
	main()
