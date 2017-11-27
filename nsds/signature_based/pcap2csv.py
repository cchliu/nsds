"""Extract packet fields from pcap and store it in csv."""
import os
import sys
import logging
from subprocess import call

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def tshark_cmd():
    """Add fields to tshark command."""
    cmd = ['tshark', '-r', 'filename', '-T', 'fields', '-E', 'separator=/t']
    csv_fields_file = "fields_convertedtocsv.txt"
    with open(csv_fields_file, 'rb') as ff:
        for line in ff:
            # Ignore the comment lines
            if len(line)>0 and line[0] != '#':
                field, ftype = line.rstrip('\n').split(',')
                cmd.append('-e')
                cmd.append(field)
    return cmd

def pcapTocsv(filename, cmd):
    """Run tshark command to generate csv output.
    
    :param filename: The filename of the pcap file to be processed.
    :param cmd: The tshark command.

    :returns: The path of the generated csv file.

    """
    csvFile = 'Traffic/{0}.csv'.format(os.path.basename(filename))
    if os.path.isfile(csvFile):
        LOG.warn("This pcap file %s has been converted to csv" % (filename))
    else:
        LOG.debug("Converting pcap file %s to csv..." % (filename))
        cmd[2] = filename
        with open(csvFile, 'wb') as ff:
            call(cmd, stdout=ff)
    return csvFile
