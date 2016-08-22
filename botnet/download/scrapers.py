""" Download botnet dataset """

from lxml import html
import requests
import urllib2
import urllib
from bs4 import BeautifulSoup
import csv
import math
import time
import os
import re
from multiprocessing import Queue, Process

def findpcap(i, sublist, out_q):
	result = []
	for url in sublist:
		url = base_url + url
		page = urllib2.urlopen(url)
		soup = BeautifulSoup(page.read())
		hrefs = soup.find_all('a')
		for entry in hrefs:
			link = entry.get('href', None)
			if link is not None and '.pcap' in link:
				result.append([os.path.join(url, link)])
		#time.sleep(6)

	out_q.put(result)

def findsubfolders():
	url = 'https://mcfp.felk.cvut.cz/publicDatasets/?C=S;O=A'
	pattern = 'CTU-Malware-Capture-Botnet'
	#page = requests.get(url)
	#tree = html.fromstring(page.content)
	
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	hrefs = soup.find_all("a")
	outfile = 'subfolders.csv'
	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter='\t', quoting = csv.QUOTE_NONE)
		
		for entry in hrefs:
			link = entry.get('href', None)
			if link is not None and pattern in link:
				writer.writerow([link])	

def findallpcaps():
	global base_url
	base_url = 'https://mcfp.felk.cvut.cz/publicDatasets/'
	infile = 'subfolders.csv'
	subfolders = []
	with open(infile, 'rb') as ff:
		reader = csv.reader(ff, delimiter='\t', quoting = csv.QUOTE_NONE)
		for line in reader:
			subfolders.append(line[0])
	
	subfolders = subfolders[:]
	num_cores = 10
	procs = []
	out_q = Queue()
	step = int(math.ceil(len(subfolders)/float(num_cores)))			
	for i in range(num_cores):
		sublist = subfolders[i*step: (i+1)*step]
		p = Process(target = findpcap, args=(i, sublist,out_q, ))
		procs.append(p)
		p.start()

	outfile = 'pcaps.csv'
	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)	
		for i in range(num_cores):
			result = out_q.get()
			writer.writerows(result)

def filterpcaps():
	years = ['2015', '2016']
	infile = 'pcaps.csv'
	result = []
	with open(infile, 'rb') as ff:
		readers = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in readers:
			flag = sum([1 for k in years if k in line[0]])
			if flag and line[0].endswith(".pcap"):
				result.append([line[0]])

	outfile = 'pcaps_filtered.csv'
	with open(outfile, 'wb') as ff:
		writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		writer.writerows(result)	

def update_progress(progress):
        progress = int(progress)
        print "\r[{0}] {1}%".format('#'*(progress/10), progress)

def downloadpcaps():
	infile = 'pcaps_filtered.csv'
	links = []
	with open(infile, 'rb') as ff:
		readers = csv.reader(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
		for line in readers:
			links.append(line[0])

	count = 0
	lenth = len(links)		
	store_dir = '/home/cchliu/SDS/input/botnet/pcap'
	for link in links:
		savename = os.path.basename(link)
		testfile = urllib.URLopener()
		testfile.retrieve(link, os.path.join(store_dir, savename))
		count += 1
	
		# print progress
		progress = float(count) / float(lenth) * 100
		if int(progress) % 10 == 0:
			update_progress(progress)
 
def main():
	filterpcaps()
	downloadpcaps()	
	
if __name__ == "__main__":
	main()
