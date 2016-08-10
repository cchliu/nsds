import csv
import numpy as np
from plots import cdf_plot

def main():
	infile = 'flow_lenth.csv'
	nums = []
	with open(infile, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			tmp_proto, tmp_num = line[0], int(line[1])
			if tmp_proto == 'tcp':
				nums.append(tmp_num)

        xscales = [i for i in range(1,10)] + [10**k for k in np.arange(1,5,0.1)]
	xtitle = 'Flow size (#packets)'
	ytitle = 'CDF'
        cdf_plot(nums, xscales, xtitle, ytitle, 'flow_size_cdf.png')

if __name__ == "__main__":
	main()
		
