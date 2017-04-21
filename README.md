# Network Security Analysis
### Traffic
The traffic traces we have were collected between 05/30/2014 and 06/04/2014. Details as shown in the table below:


| Date | Day  |No. of files| Size(GB) | Start Time | End Time | Duration(h) |
|:-----|:-----|:----------:|:---------|:----------:|:--------:|:------------|
|05/30 |Fri   |296         |275       |13:21:56    |23:30:23  |10           |
|05/31 |Sat   |262         |244       |00:02:13    |23:59:08  |24           |
|06/01 |Sun   |269         |250       |00:11:12    |23:56:54  |24           |
|06/02 |Mon   |1035        |963       |00:14:51    |23:55:52  |24           |
|06/03 |Tue   |1051        |978       |00:03:44    |23:57:11  |24           |
|06/04 |Wed   |1008        |938       |00:00:23    |18:32:44  |18.5         |

### Install Snort
Snort is an open-source signature-based detection engine. There is a very good tutorial on installing Snort (2.9.9.x) on Ubuntu 14 and 16. The tutorial link is [here](https://s3.amazonaws.com/snort-org-site/production/document_files/files/000/000/122/original/Snort_2.9.9.x_on_Ubuntu_14-16.pdf?AWSAccessKeyId=AKIAIXACIED2SPMSC7GA&Expires=1492750589&Signature=EnmI7%2B637FSX5r%2F%2FkZZm2ChzQrU%3D).

The ruleset I am using:

```
Rule Stats...
	New:-------1099
	Deleted:---310
	Enabled Rules:----10874
	Dropped Rules:----0
	Disabled Rules:---21560
	Total Rules:------32434
IP Blacklist Stats...
	Total IPs:-----23003
```
### Run traces against Snort
Test the configuration file:
```
sudo snort -T -c /etc/snort/snort.conf
```

We just want to have alerts, trying to find a way to suppress packet logging.

