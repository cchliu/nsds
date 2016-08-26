import os
import glob
import csv

def get_files(date):
	#date = '0530'
	input_dir = '/media/cchliu/disk5'
	files_lst = glob.glob('{0}/mu*2014{1}*'.format(input_dir, date))
	files_lst = sorted(files_lst)
	files_lst = [[k] for k in files_lst]

	outfile = 'pcaps_{0}.csv'.format(date)
	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		writer.writerows(files_lst)

def main():
	date = ['0530', '0531', '0601', '0602', '0603', '0604']
	for tmp_date in date:
		get_files(tmp_date)


if __name__ == "__main__":
	main()
