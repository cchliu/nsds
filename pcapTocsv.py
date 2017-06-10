"""Extract packet fields from pcap and store it in csv."""
import os
import sys
import logging
import sqlite3
from subprocess import call

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# CSV column No. of relevant fields
TIME_EPOCH = 2
IP_SRC  = 5
IP_DST  = 6
UDP_SRCPORT = 7
UDP_DSTPORT = 8
TCP_SRCPORT = 9
TCP_DSTPORT = 10
IP_PROTOCOL = 14

# Protocol Number
TCP_IP_PROTOCOL = 6
UDP_IP_PROTOCOL = 17

# Field format in the ALERT table
Five_tuples = [
    "source_ip TEXT",
    "destination_ip TEXT",
    "sport_itype INTEGER",
    "dport_icode INTEGER",
    "protocol INTEGER"
]

data_types = {
    "TEXT":str,
    "INTEGER":int
}


def tshark_cmd():
    """Add fields to tshark command."""
    cmd = ['tshark', '-r', 'filename', '-T', 'fields', '-E', 'separator=/t']
    csv_fields_file = "fields_convertedtocsv.txt"
    with open(csv_fields_file, 'rb') as ff:
        for line in ff:
            # Ignore the comment lines
            if len(line)>0 and line[0] != '#':
                cmd.append('-e')
                cmd.append(line.rstrip('\n'))
    return cmd

def pcapTocsv(filename, cmd):
    """Run tshark command to generate csv output.
    
    :param filename: The filename of the pcap file to be processed.
    :param cmd: The tshark command.

    :returns: The path of the generated csv file.
    """
    cmd[2] = filename
    csvFile = 'Traffic/{0}.csv'.format(os.path.basename(filename))
    with open(csvFile, 'wb') as ff:
        call(cmd, stdout=ff)

    return csvFile

def aggregate(csvfile):
    """Scan through the csvfile and aggregate packets under the same 5-tuples.
    
    We focus on TCP packets.

    :param csvfile: The path to the generated csv file.
    
    :returns: A dictionary with key:5-tuple and value:packet records. 
    """
    flows = {}
    with open(csvfile, 'rb') as ff:
        for row in ff:
            row = row.rstrip('\n')
            row_list = row.split('\t')
            # If it is a TCP packet
            if int(row_list[IP_PROTOCOL]) == TCP_IP_PROTOCOL:
                # We will write down bi-directional traffic under one unidirectional 5-tuple,
                # whichever direction that packet comes first. 
                curr_tuple_incoming = (row_list[IP_SRC], row_list[IP_DST], row_list[TCP_SRCPORT], \
                        row_list[TCP_DSTPORT], str(TCP_IP_PROTOCOL))
                
                curr_tuple_outgoing = (row_list[IP_DST], row_list[IP_SRC], row_list[TCP_DSTPORT], \
                        row_list[TCP_SRCPORT], str(TCP_IP_PROTOCOL))
      
                if curr_tuple_incoming in flows:
                    if not curr_tuple_outgoing in flows:
                        flows[curr_tuple_incoming].append(row)
                    else:
                        LOG.error("Duplicate 5-tuple entries for flow:%s" % (row,))
                elif curr_tuple_outgoing in flows :
                    flows[curr_tuple_outgoing].append(row)
                else:
                    flows[curr_tuple_incoming] = [row]
                
    return flows

def select_exist_cmd(inputs):
    """For each input 5-tuple, create the query command issued to the database
    to check if there is a match with the 5-tuple.

    :params inputs: The input 5-tuple.
    
    :returns: The query statement.
    """
    _conditions = []
    for idx, item in enumerate(Five_tuples):
        field, ftype = item.split(' ')
        if ftype == "TEXT":
            _conditions.append( "{0}='{1}' ".format(field, data_types[ftype](inputs[idx])))
        else:
            _conditions.append( "{0}={1} ".format(field, data_types[ftype](inputs[idx])))

    _clause = 'AND '.join(_conditions)

    table_name = "ALERT"
    _query = """SELECT EXISTS (SELECT 1 FROM %s WHERE %s LIMIT 1)""" % (table_name, _clause)
    return _query

def select_exist_coarse(ip):
    """Create the query command issued to the database to check if there is a match based
    on the source_ip/destination_ip."""

    table_name = "ALERT"

    _query = """SELECT EXISTS (SELECT 1 FROM %s WHERE source_ip="%s" OR destination_ip="%s" LIMIT 1)""" \
            % (table_name, ip, ip)
    return _query

def flow_match(conn, flow):
    """Input a 5-tuple, search the ALERT table to find if
    there is a match with the 5-tuple. 

    :params flow: The input 5-tuple.
    
    :returns: Boolean, True there is a match; False no match. 
    """
    c = conn.cursor()
    # Since bi-directional traffic is logged under one unidirectional 5-tuple,
    # we need to query 5-tuples of both direction see if there is a match.
    flow_incoming = flow
    flow_outgoing = (flow[1], flow[0], flow[3], flow[2], flow[4])

    _query = select_exist_cmd(flow_incoming)
    LOG.debug(_query)
    c.execute(_query)
    match_incoming = c.fetchone()[0]
    if match_incoming:
        return True 

    _query = select_exist_cmd(flow_outgoing)
    LOG.debug(_query)
    c.execute(_query)
    match_outgoing = c.fetchone()[0]
    if match_outgoing:
        return True
    return False

def flow_filter(conn, flows):
    """Apply a first-stage filter: aggregate 5-tuples under unique src_ips. Then
    check if this src_ip ever exists in the ALERT table (either in src_ip position or in dst_ip position). 
    If not, we save the trouble for querying the fine-grained 5-tuples in this bowl. 
    If yes, for each 5-tuple aggregated under this src_ip, we query the ALERT table to check if there is a match.

    Note because the traffic is bi-directional, the dst_ip is also src_ip in the other direction.
    """
    unique_src = {}
    for flow in flows:
        src_ip = flow[0]
        if not src_ip in unique_src:
            unique_src[src_ip] = [flow]
        else:
            unique_src[src_ip].append(flow)

    LOG.debug("No. of unique src_ips: %d" % (len(unique_src),))

    results = []
    c = conn.cursor()
    for src_ip in unique_src:
        _query = select_exist_coarse(src_ip)
        LOG.debug(_query)
        c.execute(_query)
        # If this ip exists in the ALERT table
        if c.fetchone()[0]:    
            for flow in unique_src[src_ip]:
                # If this 5-tuple matches in the ALERT table
                if flow_match(conn, flow):
                    results += flows[flow]
    return results

def flow_filter_v1(conn, flows):
    """Deprecated::too slow.
    
    For each input 5-tuple, search the ALERT table to find if 
    there is a match with the 5-tuple. Extracting the corresponding flow records 
    that trigger alerts.

    :params flows: The flow dictionary built after scanning through the csv file.
    
    :returns: A list of corresponding flow records.
    """
    c = conn.cursor()
    filtered_records = []

    for flow in flows:
        """Since bi-directional traffic is logged under one unidirectional 5-tuple,
        we need to query 5-tuples of both direction see if there is a match."""
        flow_incoming = flow
        flow_outgoing = (flow[1], flow[0], flow[3], flow[2], flow[4])

        _query = query_cmd(flow_incoming)
        LOG.debug(_query)
        c.execute(_query)
        match_incoming = c.fetchone()[0]
        if match_incoming:
            filtered_records += flows[flow]
            continue

        _query = query_cmd(flow_outgoing)
        LOG.debug(_query)
        c.execute(_query)
        match_outgoing = c.fetchone()[0]
        if match_outgoing:
            filtered_records += flows[flow]
        
    return filtered_records

def select_range_cmd(start_epoch, end_epoch):
    """Select all alerts within the time interval of a pcap file.
    
    :params start_epoch/end_epoch: The time interval of the pcap file.

    :returns: The query statement.
    """
    table_name = "ALERT" 
    _query = "SELECT event_second, event_microsecond, source_ip, destination_ip, \
        sport_itype, dport_icode, protocol FROM %s WHERE event_second >= %d \
        AND event_second <= %d" % (table_name, start_epoch, end_epoch)
      
def flow_filter_v2(conn, flows):
    """Deprecated:: This is wrong because it misses packets of flows that are across
    multiple pcap files.
    
    Select all alerts within the time interval of a pcap file. Aggregate the alerts 
    by unique 5-tuples. Then for each 5-tuple in the aggregated alerts, check if there 
    is a match in the flows.
    
    :params conn: The alert table connection.
    :params flows: The flow dictionary built after scanning through the csv file.

    :returns: A list of corresponding flow records.
    """
    # Find the start/end epoch of the pcap file.
    start_epoch, end_epoch = 1497032677, 0
    for flow in flows:
        for row in flows[flow]:
            row_list = row.split('\t')
            curr_epoch = int(float(row_list[TIME_EPOCH]))
            if curr_epoch < start_epoch:
                start_epoch = curr_epoch
            if curr_epoch > end_epoch:
                end_epoch = curr_epoch
    end_epoch += 1

    # Select all alerts within the time interval of a pcap file.
    _query = select_range_cmd(start_epoch, end_epoch)
    c = conn.cursor()
    c.execute(_query)
