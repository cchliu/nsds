import csv
import os
import glob
from read_alerts import read_alerts
import settings

def process(indir):
	files_lst = glob.glob('{0}/alert*'.format(indir))
	files_lst = [k for k in files_lst if '.csv' not in k]
	files_lst = sorted(files_lst)

	read_alerts(files_lst)	 	

def main():
	settings.init(2014, 0)
	date = ['0530', '0531', '0601', '0602', '0603', '0604']
	log_base = '/home/cchliu/work/SDS/log/wifi'
	for tmp_date in date:
		tmp_log_dir = os.path.join(log_base, tmp_date)
		process(tmp_log_dir)

		
if __name__ == "__main__":
	main()							
