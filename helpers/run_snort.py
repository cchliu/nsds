"""
	Running pcap files against SNORT
"""
import os
import glob
import csv
from subprocess import call

def run_snort(pcap_dir, log_dir, pcap_file):
        # remove old alerts in log_dir
        files_lst = glob.glob('{0}/*'.format(log_dir))
        for fname in files_lst:
                os.remove(fname)

        #files_lst = glob.glob('{0}/*'.format(pcap_dir))
        #files_lst = sorted(files_lst)

        tmp_pcap_file = pcap_file
	snort_config_path = '/etc/snort/snort.conf'
        #with open(tmp_pcap_file, 'wb') as ff:
        #        writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
        #        for fname in files_lst:
        #                writer.writerow([fname])

        my_cmd = ['sudo', 'snort', '-c', snort_config_path, '-l', log_dir, '--pcap-file={0}'.format(tmp_pcap_file)]

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


def main():
	date = ['0530']
	#date = ['0530', '0531', '0601', '0602', '0603', '0604']
	for tmp_date in date:
		pcap_dir = '/media/cchliu/disk5'
		log_dir = '/home/cchliu/work/data/log_security_ET/wifi'
		log_dir = os.path.join(log_dir, tmp_date)
		if not os.path.exists(log_dir):
			os.makedirs(log_dir)	

		pcap_file = 'pcaps_{0}.csv'.format(tmp_date)
		run_snort(pcap_dir, log_dir, pcap_file)


if __name__ == "__main__":
        main()

