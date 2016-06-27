import settings
import run_pcapTocsv
import buildcsv
import splitcap_csv
import reorder_csv
import helpers
import time
 
indir = '/home/chang/input/MuD/reorder'
def main():
	"""
	files_lst = glob.glob('{0}/*'.format(indir))
	files_lst = sorted(files_lst)
	for tmp_file in files_lst:
		base_string = os.path.basename(tmp_file)
		base_string = base_string.split('.')[0]
			
		settings.init('MuD/{0}'.format(base_string))
		run_pcapTocsv.main()
		buildcsv.main()
		buildHashdb.main()
		addHashdb.main()
		addLenthHashdb.main()		
	"""
	#settings.init('MuD/MuD2007-03-02-01')
	settings.init('test_data')

	start_time = time.time()
	run_pcapTocsv.main(settings.pcap_dir, settings.pcapTocsv_dir)
	end_time = time.time()
	print "Time elapsed for converting pcap to csv: ", end_time - start_time
	
	start_time = time.time()
	buildcsv.main(settings.pcapTocsv_dir, settings.pcap_dir, settings.db_csv_dir)
	end_time = time.time()
	print "Time elapsed for adding start_byte for csv: ", end_time - start_time

	#helpers.create_recursive_dirs(settings.HASH_DIR_LAYERS, settings.splitted_csv_dir)

	start_time = time.time()
	splitcap_csv.main(settings.splitted_csv_dir, settings.db_csv_dir, settings.HASH_LENTH, settings.HASH_DIR_LAYERS)
	end_time = time.time()
	print "Time elapsed for splitting traffic into smalle 5-tuple based pcaps: ", end_time - start_time	
	
	start_time = time.time()
	reorder_csv.main(settings.splitted_csv_dir)
	buildcsv.main(settings.splitted_csv_dir, settings.splitted_pcap_dir, settings.splitted_csv_dir)
	end_time = time.time()
	print "Time elapsed for reordering splitted csv files: ", end_time - start_time
	
		
	#splitcap.main()
	#buildcsv.main(settings.splitted_pcapTocsv_dir, settings.splitted_pcap_dir, settings.splitted_db_csv_dir)
	#addLenthHashdb.main()
	
		
if __name__ == "__main__":
	main()
