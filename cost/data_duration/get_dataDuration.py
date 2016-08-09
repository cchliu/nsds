import csv
import glob

def get_timeDuration(files_lst, date):
	startFile = files_lst[0]
	endFile = files_lst[-1]

	# frame_time_epoch in unit of seconds
	count = 0
	startTime = 0
	with open(startFile, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting=csv.QUOTE_NONE)
		for line in reader:
			if count == 0:
				startTime = float(line[2])
			count += 1
	
	endTime = 0
	with open(endFile, 'rb') as ff:
		reader = csv.reader(ff, delimiter = '\t', quoting=csv.QUOTE_NONE)
		for line in reader:
			endTime = float(line[2])
	time_duration = endTime - startTime
	print "Time duration for day {0} is {1}".format(date, time_duration)

def main():
	indir = '/home/cchliu/data/input/wifi/0530/pcapTocsv'
	files_lst = glob.glob('{0}/*.csv'.format(indir))
	files_lst = sorted(files_lst)
	get_timeDuration(files_lst, '0530')			

if __name__ == "__main__":
	main()
