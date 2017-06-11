# Network Security Analysis
### Traffic
The traffic traces we have were collected between 05/30/2014 and 06/04/2014. Each trace file is named as xx_num_YYYYmmddHHMMSS. The trace is continuous over time and across days. Details as shown in the table below:


| Date | Day  |No. of files| Size(GB) | Start Time | End Time | Duration(h) |
|:-----|:-----|:----------:|:---------|:----------:|:--------:|:------------|
|05/30 |Fri   |296         |275       |13:21:56    |23:30:23  |10           |
|05/31 |Sat   |262         |244       |00:02:13    |23:59:08  |24           |
|06/01 |Sun   |269         |250       |00:11:12    |23:56:54  |24           |
|06/02 |Mon   |1035        |963       |00:14:51    |23:55:52  |24           |
|06/03 |Tue   |1051        |978       |00:03:44    |23:57:11  |24           |
|06/04 |Wed   |1008        |938       |00:00:23    |18:32:44  |18.5         |

### Install Snort
Snort is an open-source signature-based detection engine. There is a very good tutorial on installing Snort (2.9.9.x) on Ubuntu 14 and 16. The tutorial link is [Snort 2.9.9.x on Ubuntu 14 -16](https://snort.org/documents).

The ruleset I am using:

```	
Rule Stats...
	New:-------1074
	Deleted:---285
	Enabled Rules:----11035
	Dropped Rules:----0
	Disabled Rules:---21745
	Total Rules:------32780
IP Blacklist Stats...
	Total IPs:-----20829

```
Test the configuration file:
```
sudo snort -T -c /etc/snort/snort.conf
```
### Run traces against Snort
We just want to store alerts (not pacekts). 
```
Edit snort.conf: 
output alert_unified2: filename snort.alert, limit 128
```
Run Snort as
```
sudo snort -c /etc/snort/snort.conf -u chang -g chang -N -l /tmp --pcap-file=output.txt
```
We use the following options:
```
-u chang			Run snort as the following user after startup.
-g chang			Run snort as the following group after startup.
-N				Turn off packet logging. The program still generates alerts normally.
-l /tmp				Set the output logging directory to /tmp
-c /etc/snort/snort.conf	The path to snort.conf
--pcap-file=output.txt		File that contains a list of pcaps to read. Can specify path to pcap or directory to recurse to get pcaps.
```

Some parameters need to be tuned based on the [README.stream5](http://lpc1.clpccd.cc.ca.us/lpc/jgonder/studentresources/TNT%20v.%202.6/bin/cmdlinetools/snort/doc/README.stream5):
```
Global settings for the Stream5 preprocessor
- memcap 	1073741824(maximum)

TCP Configuration for stream5_tcp
- max_queued_bytes	4194304(default * 4)
- max_queued_segs	2621(default)
```
### Create ALERT Table
We insert all "TCP" alerts into the ALERT table for later analysis. There are in total 22,465,730 alerts.
- Create an ALERT table with fields specified in the [unified2 IDS event](https://www.snort.org/faq/readme-unified2).
- Decode alert event records stored in the unified2 format.
- Load the event records into the database in chunks.
- scripts: [barnyard.py](./barnyard.py), [unified2.py](./unified2.py)

### Feasibility study over the dataset
Next we scan through the pcap files to extract corresponding flow packets.
- Convert pcap to csv
  - Remove these fields because:
```
tshark: Some fields aren't valid:
	dns.resp.primaryname
	dns.resp.ns
	dns.resp.addr
```
- For each csv file, scan through the whole file, record all unique 5-tuples; for each unique 5-tuple, check there is an alert matching with this 5-tuple.
- How long will it take to process one query? How long will it take to process one file? And how long will it take to process all pcaps?

- Load extracted packet records into a database.

### Implementation -- reactive routing/mirroring
Step #1: create topology

```
                     +-------+
---veth1-----veth0---|  OVS  |---veth2-----veth3---
                     |       |---veth4-----veth5---
		     +-------+
```

