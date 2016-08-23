import csv
import os
import glob
import numpy as np
from plots import cdf_plot_x
from plots import cdf_plot_semilogx


def find_earliest_pos_in_flow(result):
        mapping = {}
        for line in result:
                proto, src_ip, src_port, dst_ip, dst_port, time_epoch, sid, priority, classification, msg = line[:10]
                micro_flow_id, tmp_direction, pkt_in_position, micro_flow_lenth = line[-4:]
                
		# pos_in_flow starts from 0
		pkt_in_position = int(pkt_in_position)
                if proto == 'tcp' and pkt_in_position >= 0:
			tmp_string = ' '.join([proto, src_ip, src_port, dst_ip, dst_port, micro_flow_id, tmp_direction, sid])
			### debug
			#if pkt_in_position + 1 <= 2:
			#	print line
                        if not tmp_string in mapping:
                                mapping[tmp_string] = [pkt_in_position+1]
                        else:
				mapping[tmp_string].append(pkt_in_position+1)
 
       # earlist pos_in_flow for each (flow, sid) pair 
	output = [sorted(mapping[k])[0] for k in mapping]
	return output

def stats_2(files_lst, postfix):
	alerts = []
	for tmpfile in files_lst:
		with open(tmpfile, 'rb') as ff:
			reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
			for line in reader:
				alerts.append(line)
	
	# get earliest pos_in_flow for each (flow, sid) pair
	nums = find_earliest_pos_in_flow(alerts)
	xscales = [i for i in range(1,10)] + [10**k for k in np.arange(1,3,0.1)]
	xlabel = 'K parameter'
	ylabel = 'Performance of detection'
	title = ''
	outfile = 'detectability_K_cdf_{0}.png'.format(postfix)
	kwargs = {'xlabel':xlabel, 'ylabel':ylabel, 'title':title, 'outfile':outfile}
	cdf_plot_semilogx(nums, xscales, **kwargs)
	
def main():
	log_dir = '/home/cchliu/data/log_security_ET/wifi/0530'
        files_lst = glob.glob('{0}/*.csv'.format(log_dir))
        stats_2(files_lst, '0530_securityET')
		
if __name__ == "__main__":
	main()
