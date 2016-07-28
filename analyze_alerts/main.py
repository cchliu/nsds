import settings
import helpers
import run_snort
import time

def main():
	#settings.init('wifi')
	#settings.init('StratosphereIPS')
	settings.init('panda')
	helpers.create_dir(settings.log_dir)
	
	start_time = time.time()
	run_snort.main(settings.pcap_dir, settings.log_dir)
	end_time = time.time()
	print "Time elapsed for running pcap files against SNORT: ", end_time - start_time

if __name__ == "__main__":
	main()
