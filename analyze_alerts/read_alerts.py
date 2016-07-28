"""
	Create a row for each alert, including attributes:
	proto, ip_src, ip_dst, port_src, port_dst, time_epoch, SID, classification, priority, MSG
"""
import csv
import os
from parse_alerts import getSID, getMsg, getEpochTime, getIpPort, getProto, getPriority, getClassification

def read_alerts(infiles):
	# parse alerts one by one
	# extract proto, ip, port, SID, MSG, classification, priority, time
        result = []
        flag = -100
        # initialize
        proto, src_ip, dst_ip, src_port, dst_port, time_epoch, sid, msg, priority, classification = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        for tmp_file in infiles:
                with open(tmp_file, 'rb') as ff:
                        for row in ff:
                                row = row.rstrip('\n')
                                if row[0:4] == "[**]":
                                        sid = getSID(row)
                                        msg = getMsg(row)
                                        flag = 1
                                        continue
                                if flag == 1:
                                        classification = getClassification(row)
                                        priority = getPriority(row)
                                        flag = 2
                                        continue
                                if flag == 2:
                                        time_epoch = getEpochTime(row)
                                        (src_ip, src_port, dst_ip, dst_port) = getIpPort(row)
                                        flag = 3
                                        continue
                                if flag == 3:
                                        proto = getProto(row)
                                        flag = -100
					tmp = [proto, src_ip, src_port, dst_ip, dst_port, time_epoch, sid, classification, priority, msg]
					result.append(tmp)
	
		outfile = tmp_file + '.csv'
		with open(outfile, 'wb') as ff:
			writer = csv.writer(ff, delimiter = '\t', quoting = csv.QUOTE_NONE)
			writer.writerows(result)

if __name__ == "__main__":
	pass
