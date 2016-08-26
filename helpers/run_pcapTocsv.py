"""
	Extract packet fields from pcap and store it in csv
"""
import os
import glob
import csv
import math
from subprocess import call
from multiprocessing import Process, Queue

def update_progress(progress):
        progress = int(progress)
        print "\r[{0}] {1}%".format('#'*(progress/10), progress)

def worker(sublist, cmd, pcapTocsv_dir, out_q, thread_id):	
	count = 0
	lenth = len(sublist)
	for tmp_file in sublist:
		count += 1
		my_cmd = cmd
		my_cmd[2] = tmp_file
	
		out_fname = os.path.join(pcapTocsv_dir, os.path.basename(tmp_file)+'.csv')	
		print out_fname
		with open(out_fname, 'wb') as ff:
			call(my_cmd, stdout=ff)		
		
		#percentg = int(math.floor(count / float(lenth) * 100))
		#if percentg % 10 == 0:
		#	print "Progress on thread {0}".format(thread_id)
		#	update_progress(percentg)			 
	out_q.put(1)
		
def run_pcapTocsv(files_lst, pcapTocsv_dir, numproc):
	# no need to remove old files in pcapTocsv_dir because of 'wb' mode
	#files_lst = glob.glob('{0}/*'.format(pcap_dir))
	#files_lst = sorted(files_lst)

	tmp_file = '' 
	my_cmd = ['tshark', '-r', tmp_file, '-T', 'fields', '-E', 'separator=/t']
	with open(fields_convertedtocsv_file, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			# remove the comment lines
			if len(line) > 0 and line[0][0] != '#':
				my_cmd.append('-e')
				my_cmd.append(line[0])
			
	# parallelization starts here
	#numproc = 20
	out_q = Queue()
	chunksize = int(math.ceil(len(files_lst) / float(numproc)))
	procs = []
	for i in range(numproc):
		sublist = files_lst[i*chunksize:(i+1)*chunksize]
		p = Process(target = worker, args = (sublist, my_cmd, pcapTocsv_dir, out_q, i))
		procs.append(p)
		p.start()

	for i in range(numproc):
		out_q.get()

def main():
	global fields_convertedtocsv_file
	fields_convertedtocsv_file = 'fields_convertedtocsv.txt'

	#date = ['0602', '0603', '0604']
	date = ['0603', '0604']
	pcap_dir = '/media/cchliu/disk5'
	pcapTocsv_dir = '/home/cchliu/work/SDS/input/wifi/pcapTocsv'
	
	for tmp_date in date:
		tmp_path = os.path.join(pcapTocsv_dir, tmp_date)
		if not os.path.exists(tmp_path):
			os.makedirs(tmp_path)
	
	numprocs = 5
	step = 300
	for tmp_date in date:
		print "currently processing files of {0}".format(tmp_date)
		files_lst = []
		pcap_file = 'pcaps_{0}.csv'.format(tmp_date)
		with open(pcap_file, 'rb') as ff:
			reader = csv.reader(ff, delimiter= '\t', quoting = csv.QUOTE_NONE)
			for line in reader:
				files_lst.append(line[0])
		files_lst = sorted(files_lst)
		
		for i in range(5):
			subfiles_lst = files_lst[i*step : (i+1)*step]
			tmp_pcapTocsv_dir = os.path.join(pcapTocsv_dir, tmp_date)
			run_pcapTocsv(subfiles_lst, tmp_pcapTocsv_dir, numprocs)
			
			# zip csv files to save space
			csvfiles_lst = glob.glob('{0}/*.csv'.format(tmp_pcapTocsv_dir))
			if len(csvfiles_lst) != 0:
				tar_cmd = ['tar',  '-zcvf', '{0}/tarfile_{1}_to_{2}.tar.gz'.format(tmp_pcapTocsv_dir, i*step, (i+1)*step)] + csvfiles_lst
				call(tar_cmd)
				rm_cmd = ['rm'] + csvfiles_lst
				call(rm_cmd)

if __name__ == "__main__":
	main()	
