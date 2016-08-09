""" Get Num of Packets """
import os
import csv
import math
from multiprocessing import Process, Queue


def worker_pcktNum(subfiles, out_q, thread_id):
	count = 0
	count_udp_tcp = 0
	count_udp = 0
	count_tcp = 0
	for tmpfile in subfiles:
		with open(tmpfile, 'rb') as ff:
			reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
			for line in reader:
				count += 1
				frame_number, frame_time, frame_time_epoch, frame_lenth, frame_proto, src_ip, dst_ip, src_udp_port, dst_udp_port, src_tcp_port, dst_tcp_port, tcp_flags_syn, tcp_flags_ack = line[:13]
				if 'udp' in frame_proto:
					count_udp_tcp += 1
					count_udp += 1
				elif 'tcp' in frame_proto:
					count_udp_tcp += 1
					count_tcp += 1 
				else:
					print frame_proto
	out_q.put((count, count_udp_tcp, count_udp, count_tcp))

def processing(files, num_of_procs):
	### num of packets
	out_q = Queue()
	
	chunksize = int(math.ceil(len(files) / float(num_of_procs)))
	procs = []
	for i in range(num_of_procs):
		sublist = files[i*chunksize: (i+1)*chunksize]
		p = Process(target = worker_pcktNum, args =(sublist, out_q, i,))
		procs.append(p)
		p.start()

	count = 0
	count_udp_tcp = 0
	count_udp = 0
	count_tcp = 0
	for i in range(num_of_procs):
		num1, num2, num3, num4 = out_q.get()
		count += num1
		count_udp_tcp += num2
		count_udp += num3
		count_tcp += num4

	outfile = 'pcktNum.csv'
	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		str1 = 'Total num of pckts: {0}'.format(count)
		str2 = 'Total num of udp/tcp pckts: {0}'.format(count_udp_tcp)
		str3 = 'Total num of tcp pckts: {0}'.format(count_tcp)
		str4 = 'Total num of udp pckts: {0}'.format(count_udp)
		writer.writerows([[str1], [str2], [str3], [str4]])

def main():
	indir = "/home/cchliu/data/input/wifi/0530/splitcsv"
	files = []
	for root, dirnames, filenames in os.walk(indir):
		for filename in filenames:
			files.append(os.path.join(root, filename))
	processing(files, 10)	

if __name__ == "__main__":
	main()	
