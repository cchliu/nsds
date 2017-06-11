"""Scan through traffic traces and extract those flows that are corresponding to the alerts."""
import sys
import logging
import sqlite3

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

def aggregate_per_file(csvfile, flows):
    """Scan through the csvfile and aggregate packets under the same 5-tuples.
    
    We focus on TCP packets.

    :param csvfile: The path to the generated csv file.
    :param flows: The dictionary with key:5-tuple and value:packet records.
    
    """
    #flows = {}
    LOG.debug("Aggregating traffic from file %s" % (csvfile))
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


def aggregate_traffic(csvfiles):
    """Scan through a list of csvfiles and aggregate packets under the same 5-tuples.

    :param csvfiles: A list of csvfiles.

    :returns: A dictionary with key:5-tuple and value:packet records.
    """
    flows = {}
    for csvfile in csvfiles:
        aggregate_per_file(csvfile, flows)
    return flows


def aggregate_alerts():
    """ Read all alerts from the ALERT table and aggregate alerts under the same 5-tuples."""
    sqlite_file = 'alert.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    table_name = "ALERT"
    _query = "SELECT source_ip, destination_ip, sport_itype, dport_icode, protocol FROM %s" % (table_name)
    c.execute(_query)

    aggregated_alerts = {}
    for row in c:
        # We log bi-directional alerts under one uni-directional 5-tuple.
        flow = [str(k) for k in row]
        incoming_flow = flow
        outgoing_flow = [flow[1], flow[0], flow[3], flow[2], flow[4]]
        incoming_tuple = tuple(incoming_flow)
        outgoing_tuple = tuple(outgoing_flow)
        if incoming_tuple in aggregated_alerts:
            continue
        if outgoing_tuple in aggregated_alerts:
            continue
        aggregated_alerts[incoming_tuple] = 1

    LOG.debug("No. of aggregated alerts: %d" % (len(aggregated_alerts)))
    return aggregated_alerts

def filter_flows(flows, aggregated_alerts):
    """For each 5-tuple in aggregated_alerts, check if there is a match in flows.
    
    :param flows: A dictionary with key:5-tuple and value:packet records.
    :param aggregated_alerts: A dictionary with unique 5-tuples among the alerts.

    "returns: A list of packet records.

    """
    result = []
    # We log bi-directional traffic under one uni-directional 5-tuple.
    # We log bi-directional alerts under one uni-directional 5-tuple.
    for flow in aggregated_alerts:
        incoming_flow = flow
        outgoing_flow = (flow[1], flow[0], flow[3], flow[2], flow[4])
        if incoming_flow in flows:
            result += flows[incoming_flow]
            continue
        if outgoing_flow in flows:
            result += flows[outgoing_flow]
            continue
    LOG.info("No. of corresponding packets: %d" % (len(result)))
    return result

    

