""" 
	No. of distinct unique 5-tuples (micro flow_id, sid) 
	No. of alerts
	No. of distinct SIDs triggered
"""
import csv
import os
import glob

def count_alerts(result):
	return len(result)

def count_unique_5tuple(result):
	mapping = {}
	for line in result:
		proto, src_ip, src_port, dst_ip, dst_port, time_epoch, sid, classification, priority, msg = line
		tmp_string = ' '.join([proto, src_ip, src_port, dst_ip, dst_port, sid])
		if not tmp_string in mapping:
			mapping[tmp_string] = 1
	return len(mapping.keys())

def count_distinct_SIDs(result):
	mapping = {}
	for line in result:
		proto, src_ip, src_port, dst_ip, dst_port, time_epoch, sid, classification, priority, msg = line
		if not sid in mapping:
			mapping[sid] = 1
	return len(mapping.keys())

def table_sid_frequency(result):
	# column: sid, No. of alerts within sid, No. of unique 5-tuples within sid,
	# sorted by No. of unique 5-tuples within sid
	mapping = {}
	for line in result:
		proto, src_ip, src_port, dst_ip, dst_port, time_epoch, sid, classification, priority, msg = line
		tmp_tuple = (sid, classification, priority, msg)
		if not tmp_tuple in mapping:
			mapping[tmp_tuple] = [line]
		else:
			mapping[tmp_tuple].append(line)
	
	entries = []
	for tmp_tuple in mapping:
		sid, classification, priority, msg = tmp_tuple
		entries += [[int(sid), count_alerts(mapping[tmp_tuple]), count_unique_5tuple(mapping[tmp_tuple]), classification, priority, msg]]
	entries.sort(key=lambda x:x[2], reverse=True)	
	
	outfile = 'table_sid_frequency.csv'
	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter='\t', quoting = csv.QUOTE_NONE)
		writer.writerows(entries)	

def stats_1(infiles):
	result = []
	for tmp_file in infiles:
		with open(tmp_file, 'rb') as ff:
			reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
			for line in reader:
				result.append(line)

	print "Number of alerts triggered: ", count_alerts(result)
	print "Number of unique 5-tuples (micro flow_id, sid): ", count_unique_5tuple(result)	
	table_sid_frequency(result)

def main():
	date = ['0530', '0531', '0601', '0602', '0603', '0604']
	#date = ['0530']
	log_base = '/home/cchliu/work/SDS/log/wifi'

	files_lst = []
	for tmp_date in date:
		log_dir = os.path.join(log_base, tmp_date)
		tmp_files_lst = glob.glob('{0}/*.csv'.format(log_dir))
		files_lst += tmp_files_lst

	stats_1(files_lst)

if __name__ == "__main__":
	main()
	
