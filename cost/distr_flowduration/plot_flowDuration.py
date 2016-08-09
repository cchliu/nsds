import csv
import numpy as np
from plots import cdf_plot_x
from plots import xy_plot
from plots import cdf_plot_semilogx

def main():
	infile = 'flow_duration.csv'
	nums = []
	with open(infile, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			tmp_proto, tmp_num = line[0], float(line[1])
			if tmp_proto == 'tcp':
				nums.append(tmp_num)

	### some simple stats
	print "Avg flow duration: ", sum(nums)/float(len(nums))

	### plot distribution
        xscales = [10**k for k in np.arange(0,5,0.1)]
	xtitle = 'Flow duration (#seconds)'
	ytitle = 'CDF'
        cdf_plot_semilogx(nums, xscales, xtitle, ytitle, 'flow_duration_cdf.png')

if __name__ == "__main__":
	main()
		
