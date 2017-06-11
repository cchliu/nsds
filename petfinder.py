"""Convert pcap to csv; Extract packets that are corresponding to
the alerts; Load filtered packets to the database.

Usage:: python petfinder.py 

"""
import os
import re
import sys
import time
import logging
import sqlite3

import pcap2csv
import extract_flows
import csv2sqlite

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def get_pcapFiles(indir_pcap):
    """Get a list of pcap files that are to be processed.

    :param indir_pcap: The directory of pcap files.
    
    :returns: A list of pcap files to be processed.

    """
    files = []
    for dirname, subdir, filelist in os.walk(indir_pcap):
        files += [os.path.join(dirname, f) for f in filelist if os.path.isfile(os.path.join(dirname, f))]
    files = sorted(files)

    pattern = "mu_"
    selected_files = []
    for filename in files:
        if re.findall(pattern, filename):
            selected_files.append(filename)
    # Important!!! Sort the pcap files in order.
    files = sorted(selected_files)
    return files

def chunks(data, rows = 20):
    """Process the pcap files in batch. Batch size = 20 by default"""
    for i in xrange(0, len(data), rows):
        yield data[i:i+rows]

def petfinder(chunk, aggregated_alerts):
    """Convert pcap to csv; Extract packets that are corresponding to the alerts.

    :param chunk: A batch of pcap files to process.

    :returns: A list of packet records.

    """
    tshark_cmd = pcap2csv.tshark_cmd()
    csvfiles = []
    # Convert pcap to csv
    for filename in chunk:
        csvfile = pcap2csv.pcapTocsv(filename, tshark_cmd)        
        csvfiles.append(csvfile)

    # Filter flows
    flows = extract_flows.aggregate_traffic(csvfiles)
    records = extract_flows.filter_flows(flows, aggregated_alerts)
    return records 
    
def main():
    # The input directory for pcap files.
    indir_pcap = '/media/chang/disk5/'
    pcapfiles = get_pcapFiles(indir_pcap)
    pcapfiles = pcapfiles[:20]
    LOG.info("No. of pcap files to be processed: %d" % (len(pcapfiles)))

    # Aggregate alerts under unique 5-tuples.
    aggregated_alerts = extract_flows.aggregate_alerts()

    # Create the TRACE table
    sqlite_file = "trace.sqlite"
    table_name = "TRACE"
    conn = sqlite3.connect(sqlite_file)
    conn.text_factory = str
    _cast = csv2sqlite.create_table(conn, table_name)

    start_time = time.time()
    divFiles = chunks(pcapfiles)
    for chunk in divFiles:
        records = petfinder(chunk, aggregated_alerts) 
        # Load filtered packets into the TRACE table.
        csv2sqlite.insert_packets(records, _cast, conn, table_name)
    end_time = time.time()
    LOG.info("Time elapsed: %f" % (end_time - start_time))

if __name__ == "__main__":
    main()

