import socket
import time

# To receive all Ethernet protocols
ETH_P_ALL = 3

def mirror(interface, MTU):
	print "Python sniffer: "
	# Create a raw socket for sending
	s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
	s.bind((interface, 0))

	# Create a raw socket and bind it to the public interface
	srecv = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
	srecv.bind((interface, ETH_P_ALL))

	""" 
	Workaround is to create two sockets (one for sending, one for receiving) 
	# TODO:don't know why there are some packets in the beginning
	wait_time = 10
	packet, address = srecv.recvfrom(MTU)
	print packet
	time.sleep(wait_time)
	"""
	print "...Now please send packets..."

	count = 0
	while True:
		packet, sa_ll = srecv.recvfrom(MTU)
		# outgoing packets
		if sa_ll[2] == socket.PACKET_OUTGOING:
			#print "outgoing packet"
			continue
		else:
			if not len(packet) > 0:
				continue
			count += 1
			print count
			s.send(packet)

if __name__ == "__main__":
	interface = 's1-eth1'
	mirror(interface, 65535)
			
