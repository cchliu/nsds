"""Extract packet fields from pcap and store it in csv."""
import os
import sys
import logging
import sqlite3
from subprocess import call

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# CSV column No. of relevant fields
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
                        row_list[TCP_DSTPORT], TCP_IP_PROTOCOL)
                
                curr_tuple_outgoing = (row_list[IP_DST], row_list[IP_SRC], row_list[TCP_DSTPORT], \
                        row_list[TCP_SRCPORT], TCP_IP_PROTOCOL)
      
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

def query_cmd(inputs):
    """For eaach input 5-tuple, create the query command issued to the database
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
    
def flow_filter(conn, flows):
    """For each input 5-tuple, search the ALERT table to find if 
    there is a match with the 5-tuple. Extracting the corresponding flow records 
    that trigger alerts.

    :params flows: The flow dictionary built after scanning through the csv file.
    
    :returns: A list of corresponding flow records.
    """
    c = conn.cursor()
    filtered_records = []

    for flow in flows:
        """Since bidirectional traffic is logged under one unidirectional 5-tuple,
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


            




















