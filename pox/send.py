import socket
import csv
import time

# To receive all Ethernet protocols
ETH_P_ALL = 3

def recv(srecv, MTU):
	while True:
		packet, sa_ll = srecv.recvfrom(MTU)
		if sa_ll[2] == socket.PACKET_OUTGOING:
			#print "outgoing packet"
			continue
		else:
			if not len(packet) > 0:
				continue
			return
 
def send_raw(pcapfile, csvfile, interface, MTU, Limit):
	# Create raw socket
	s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
	s.bind((interface, 0))

	# Create a raw socket for receiving 
	srecv = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
	srecv.bind((interface, ETH_P_ALL))
	print "...Ready to send packets from sender side..."

	# open pcapfile
	try:
		fpcap = open(pcapfile, 'rb')
		# read out global header of pcap file
		fpcap.read(24) 
	except OSError:
		print "Pcapfile do not exisit"
		
 	# send packets in pcapfile
	count = 0
	with open(csvfile, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			count += 1
			frame_number, start_byte, pckt_size = line[-3:]
			frame_number, start_byte, pckt_size = int(frame_number), int(start_byte), int(pckt_size)
			# read out packet header due to pcap file
			fpcap.read(16)
			payload = fpcap.read(pckt_size - 16)
			s.send(payload)
	 		
			# received the packet just sent?
			recv(srecv, MTU)
			if count > Limit:
				break
	fpcap.close()
	s.close()

def main():
	pcapfile = '/home/cchliu/data/input/wifi/0530/pcap/mu_03284_20140530132156'
	csvfile = '/home/cchliu/data/input/wifi/0530/pcapTocsv/mu_03284_20140530132156.csv'
	interface = 'h1-eth0'
	MTU = 65535
	Limit = 20
	send_raw(pcapfile, csvfile, interface, MTU, Limit)
	
if __name__=="__main__":
	main()
		
