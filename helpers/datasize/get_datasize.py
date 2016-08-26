import csv
import os

def get_datasize(infile):
	total_size = 0
	with open(infile, 'rb') as ff:
		reader = csv.reader(ff, delimiter='\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			tmpfile = line[0]
			# get filesize in bytes
			total_size += os.path.getsize(tmpfile)
	print "Total data size for {0} is {1}".format(infile.rstrip('csv'), total_size)
	
def main():
	infile = 'pcaps_0530.csv'
	get_datasize(infile)			

if __name__ == "__main__":
	main()
