import re
import os

def durationOfDay(flist):
    pattern = r'(2014\d{4})(\d{6})'
    dod = {}
    for line in flist:
        match = re.findall(pattern, line)[0]    
        date = match[0]
        time = match[1]
        if not date in dod:
            dod[date] = {}
            dod[date]['start'] = time
            dod[date]['end'] = time
        dod[date]['end'] = time

    for day in sorted(dod.keys()):
        print "On date {0}, start is: {1}, end is: {2}".format(day,
                dod[day]['start'], dod[day]['end'])  

def sizeOfDay(flist):
    pattern = r'2014\d\d\d\d'
    sod = {}
    for line in flist:
        match = re.findall(pattern, line)[0]
        tmp = os.stat(line).st_size
        if not match in sod:
            sod[match] = tmp
        else:
            sod[match] += tmp     
        
    for day in sorted(sod.keys()):
        print "Size of traffic data in Day {0} is {1}GB".format(day, sod[day]/(1024**3))

def filesOfDay(flist):
    pattern = r'2014\d\d\d\d'
    fod = {}
    for line in flist:
        match = re.findall(pattern, line)[0]
        if not match in fod:
            fod[match] = 1
        else:
            fod[match] += 1
    
    for day in sorted(fod.keys()):
        print "No. of files in Day {0} is: {1}".format(day, fod[day])     

def load():
    infile = 'output.txt'
    flist = []
    with open(infile, 'rb') as ff:
        for line in ff:
            line = line.rstrip('\n')
            flist.append(line)
    
    return flist

def main():
    flist = load() 
    filesOfDay(flist)
    sizeOfDay(flist)   
    durationOfDay(flist)

if __name__ == '__main__':
    main()
