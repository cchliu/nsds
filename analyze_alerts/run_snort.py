"""
	Running pcap files against SNORT
"""
import os
import glob
import csv
import settings
from subprocess import call

def main(pcap_dir, log_dir):
	# remove old alerts in log_dir
	files_lst = glob.glob('{0}/*'.format(log_dir))
	for fname in files_lst:
		os.remove(fname)
		
	files_lst = glob.glob('{0}/*'.format(pcap_dir))
        files_lst = sorted(files_lst)

	tmp_pcap_file = 'pcap_file.txt'
	with open(tmp_pcap_file, 'wb') as ff:
		writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for fname in files_lst:
			writer.writerow([fname])

	my_cmd = ['sudo', 'snort', '-c', settings.snort_config_path, '-l', log_dir, '--pcap-file={0}'.format(tmp_pcap_file)]
	
	tmp_snort_log = 'tmp_snort_log.txt'
	with open(tmp_snort_log, 'wb') as ff:
		call(my_cmd, stdout=ff, stderr=ff)

	with open(tmp_snort_log, 'rb') as ff:
		for line in ff:
			pass
		last = line.rstrip('\n')
		print last
		checker = last == "Snort exiting"
		print checker

if __name__ == "__main__":
	pass
