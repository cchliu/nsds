""" 
	Define all global variables
"""
def init(dirname):
	### fields_convertedtocsv file
	global fields_convertedtocsv_file
	fields_convertedtocsv_file = 'fields_convertedtocsv.txt'

	### PCAP file format
	global MAX_PKT_SIZE, GLOBAL_HEADER, PKT_HEADER
	MAX_PKT_SIZE = 65535
	GLOBAL_HEADER = 24
	PKT_HEADER = 16

	### hash parameters
	global HASH_LENTH, HASH_DIR_LAYERS
	HASH_DIR_LAYERS = 3
	HASH_LENTH = 5
	
	global pcap_dir, pcapTocsv_dir, db_csv_dir, splitted_pcap_dir, splitted_csv_dir, splitted_pcapTocsv_dir, splitted_db_csv_dir
	global hashdb_csv_dir, hashdb_csv_added_dir, hashdb_csv_lenth_added_dir 
	### defining directory parameters
	pcap_dir = '/home/cchliu/work/SDS/input/{0}/pcap'.format(dirname)
	pcapTocsv_dir = '/home/cchliu/work/SDS/input/{0}/pcapTocsv'.format(dirname)
	db_csv_dir = '/home/cchliu/work/SDS/input/{0}/db_csv'.format(dirname)
	splitted_csv_dir = '/home/cchliu/work/SDS/input/{0}/splitted_csv'.format(dirname)
	splitted_pcap_dir = '/home/cchliu/work/SDS/input/{0}/splitted_pcap'.format(dirname)
	"""
	pcap_dir = '/home/chang/input/{0}/pcap'.format(dirname)			# where pcaps store
	pcapTocsv_dir = '/mnt/ssd/chang/input/{0}/pcapTocsv'.format(dirname)	# where csvs converted from pcap store
	db_csv_dir = '/mnt/ssd/chang/input/{0}/db_csv'.format(dirname)		# where db read csvs from 
	splitted_pcap_dir = '/home/chang/input/{0}/splitted_pcap'.format(dirname)	# where flow-based splitted pcaps store
	splitted_csv_dir = '/mnt/ssd/chang/input/{0}/splitted_csv'.format(dirname)	# where flow-based splitted csvs store

	splitted_db_csv_dir = '/home/chang/input/{0}/splitted_db_csv'.format(dirname)	# where modified (db) csvs for flow-based splitted pcaps store
	hashdb_csv_dir = '/home/chang/input/{0}/hashdb_csv'.format(dirname)	# where group traffic headers based on unique five-tuples
	
	# where traffic headers belonging to the same unique five-tuples are grouped together and pkt_position_in_flow and micro_flow_index added
	hashdb_csv_added_dir = '/home/chang/input/{0}/hashdb_csv_added'.format(dirname)

	# where add micro flow length (total pkts number) to each packet belonging to this micro flow
	hashdb_csv_lenth_added_dir = '/home/chang/input/{0}/hashdb_csv_lenth_added'.format(dirname)
	"""

 

