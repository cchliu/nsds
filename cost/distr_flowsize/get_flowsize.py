""" Get Num of Packets """
import os
import csv
import math
from multiprocessing import Process, Queue


def worker_flowLenth(subfiles, out_q, thread_id):
	result = []
	for tmpfile in subfiles:
		count_flow = {}
		with open(tmpfile, 'rb') as ff:
			reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
			for line in reader:
				frame_number, frame_time, frame_time_epoch, frame_lenth, frame_proto, src_ip, dst_ip, src_udp_port, dst_udp_port, src_tcp_port, dst_tcp_port, tcp_flags_syn, tcp_flags_ack = line[:13]
				micro_flow_id, direction, pos_in_flow, micro_flow_lenth = line[-4:]
				if 'udp' in frame_proto:
					tmp_proto = 'udp'
					tmp_src_port = src_udp_port
					tmp_dst_port = dst_udp_port
				elif 'tcp' in frame_proto:
					tmp_proto = 'tcp'
					tmp_src_port = src_tcp_port
					tmp_dst_port = dst_tcp_port
				else:
					print frame_proto
				tmp_string = ' '.join([tmp_proto, src_ip, tmp_src_port, dst_ip, tmp_dst_port, micro_flow_id, direction])
				if not tmp_string in count_flow:
					count_flow[tmp_string] = 1
				else:
					count_flow[tmp_string] += 1
		result += [[k.split(' ')[0], count_flow[k]] for k in count_flow.keys()]
	out_q.put(result)

def processing(files, num_of_procs):
	### lenth of flow (unique 5-tuples)
	out_q = Queue()
	chunksize = int(math.ceil(len(files) / float(num_of_procs)))
        procs = []
        for i in range(num_of_procs):
                sublist = files[i*chunksize: (i+1)*chunksize]
                p = Process(target = worker_flowLenth, args =(sublist, out_q, i,))
                procs.append(p)
                p.start()

	outfile = 'flow_lenth.csv'
	try:
		os.remove(outfile)
	except:
		pass
	with open(outfile, 'ab') as ff:
		writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for i in range(num_of_procs):
			tmp_result = out_q.get()
			writer.writerows(tmp_result)
		
def main():
	indir = "/home/cchliu/data/input/wifi/0530/splitcsv"
	files = []
	for root, dirnames, filenames in os.walk(indir):
		for filename in filenames:
			files.append(os.path.join(root, filename))
	processing(files, 10)	

if __name__ == "__main__":
	main()	
