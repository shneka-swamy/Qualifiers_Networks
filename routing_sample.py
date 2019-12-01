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
		
		self.sendReply(device)

	def declareSource(self, device, dest):
		self.isSource = True
		self.generateRREQ(device, dest)


	def sendReply(self, device):

		print("Waiting for data...\n")
		flag = True

		while flag:
			xbee_message = device.read_data()

			if xbee_message is not None:
				string_val = xbee_message.data.decode().split()
				print("Printing received data")
				print(string_val)

				



def main():


	# To open the Xbee device and to work with it

	device = XBeeDevice("/dev/ttyUSB2", 115200)


	device.open()
	print(device.get_power_level())
	rreq = RouteFormation(device)	
	rreq.createTable(device)

	rreq.declareSource(device, ['0013A20040B317F6', '0013A2004102FC76'])

	device.close()

if __name__ == "__main__":
	main()
