import csv

def get_flowNum(infile):
	count = 0
	count_tcp = 0
	count_udp = 0
	
	with open(infile, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			count += 1
			proto = line[0]
			if proto == 'tcp':
				count_tcp += 1
			elif proto == 'udp':
				count_udp += 1
			else:
				print "Unknown proto: ", proto

	return (count, count_tcp, count_udp)

def main():
	infile = 'flow_lenth.csv'
	count, count_tcp, count_udp = get_flowNum(infile)
	print "Total # of flows: ", count
	print "# of TCP flows: ", count_tcp
	print "# of UDP flows: ", count_udp

if __name__ == "__main__":
	main()			
