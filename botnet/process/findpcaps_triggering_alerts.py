import os
import glob
import csv

def filterpcaps(indir):
	files= glob.glob('{0}/*'.format(indir))
	flag = sum([1 for k in files if 'snort.log.' in k])
	return flag

def main():
	log_base = '/home/cchliu/data/log_nopolicy_ET/botnet'
	subfolders = [os.path.join(log_base,k) for k in os.listdir(log_base) if os.path.isdir(os.path.join(log_base, k))]
	print "Total number of datasets: ", len(subfolders)

	outfile = 'pcaps_triggering_alerts_nopolicy_ET.csv'
	result = []
	for subfolder in subfolders:
		if filterpcaps(subfolder):
			result.append([os.path.basename(subfolder)])
		else:
			print "Dataset not triggering an alert: ", subfolder

	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter='\t', quoting = csv.QUOTE_NONE)
		writer.writerows(result)

if __name__ == "__main__":
	main()
