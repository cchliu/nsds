"""
    Abbrevated version of unified2.py
    Credit to https://github.com/jasonish/py-idstools/blob/master/idstools/unified2.py
"""
import os
import sys
import logging
import struct
import socket
import fnmatch

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Record header length
HDR_LEN = 8

# Record types.
EVENT           = 7
EVENT_IP6       = 72
EVENT_V2        = 104
EVENT_V2_IP6    = 105

RECORD_TYPES = [
    EVENT,
    EVENT_IP6,
    EVENT_V2,
    EVENT_V2_IP6,
]

class UnknownRecordType(Exception):
    def __init__(self, record_type):
        super(UnknownRecordType, self).__init__(
            "Unknown record type: %d" % (record_type))


class Field(object):
    """ A class to represent a field in a unified2 record. Used for
    building the decoders. """
    def __init__(self, name, length, fmt=None):
        self.name = name
        self.length = length
        # An underscore (_) at the beginning is used to denote private variables
        self._fmt = fmt

    @property
    def fmt(self):
        """Builds a format string for struct.unpack."""
        if self._fmt:
            return self._fmt
        elif self.length == 4:
            return "L"
        elif self.length == 2:
            return "H"
        elif self.length == 1:
            return "B"
        else:
            return None    


# Fields in a EVENT record
EVENT_FIELDS = (
    Field("sensor-id", 4),
    Field("event-id", 4),
    Field("event-second", 4),
    Field("event-microsecond", 4),
    Field("signature-id", 4),
    Field("generator-id", 4),
    Field("signature-revision", 4),
    Field("classification-id", 4),
    Field("priority", 4),
    Field("source-ip.raw", 4, "4s"),
    Field("destination-ip.raw", 4, "4s"),
    Field("sport-itype", 2),
    Field("dport-icode", 2),
    Field("protocol", 1),
    Field("impact-flag", 1),
    Field("impact", 1),
    Field("blocked", 1),
)

# Fields for an IPv6 event.
EVENT_IP6_FIELDS = (
    Field("sensor-id", 4),
    Field("event-id", 4),
    Field("event-second", 4),
    Field("event-microsecond", 4),
    Field("signature-id", 4),
    Field("generator-id", 4),
    Field("signature-revision", 4),
    Field("classification-id", 4),
    Field("priority", 4),
    Field("source-ip.raw", 16, "16s"),
    Field("destination-ip.raw", 16, "16s"),
    Field("sport-itype", 2),
    Field("dport-icode", 2),
    Field("protocol", 1),
    Field("impact-flag", 1),
    Field("impact", 1),
    Field("blocked", 1),
)

# Fields in a v2 event.
EVENT_V2_FIELDS = EVENT_FIELDS + (
    Field("mpls-label", 4),
    Field("vlan-id", 2),
    Field("pad2", 2),
)

# Fields for an IPv6 v2 event.
EVENT_V2_IP6_FIELDS = EVENT_IP6_FIELDS + (
    Field("mpls-label", 4),
    Field("vlan-id", 2),
    Field("pad2", 2),
)


class Event(dict):
    """Event presents a unified2 event record with a dict-like 
    interface. The unified2 file format specifies multiple types of 
    event records, idstools normalizes them into a single type.

    """
    _template = {
        "sensor-id": None,
        "event-id": None,
        "event-second": None,
        "event-microsecond": None,
        "signature-id": None,
        "generator-id": None,
        "signature-revision": None,
        "classification-id": None,
        "priority": None,
        "source-ip.raw": b"",
        "destination-ip.raw": b"",
        "sport-itype": None,
        "dport-icode": None,
        "protocol": None,
        "impact-flag": None,
        "impact": None,
        "blocked": None,
        "mpls-label": None,
        "vlan-id": None,
        "pad2": None,
        "appid": None,
    }
    
    def __init__(self, event):
        self.update(self._template)
        self.update(event)

        # Create fields to hold extra data and packets associated with
        # this event
        self["packets"] = []
        self["extra-data"] = []              


class Unkown(object):
    """Class to represent an unknown record type.
    
    In the unlikely case that a record is of an unknown type, an 
    instance of 'Unknown' will be used to hold the record type and
    buffer.
    """
    def __init__(self, record_type, buf):
        """
        :param type: The record type.
        "param buf: The record buffer.
        """
        self.record_type = record_type
        self.buf = buf


class AbstractDecoder(object):
    """ Base class for decoders. """
    def __init__(self, fields):
        self.fields = fields

        # Calculate the length of the fixed portion of the record.
        self.fixed_len = sum([field.length for field in self.fields if field.length is not None])

        # Build the format string.
        self.format = ">" + "".join([field.fmt for field in self.fields if field.fmt])


class EventDecoder(AbstractDecoder):
    """ Decoder for event type records. """
    def decode(self, buf):
        """Decodes a buffer into an :class:'.Event' object."""
        values = struct.unpack(self.format, buf[0:self.fixed_len])
        keys = [field.name for field in self.fields]
        event = dict(zip(keys, values))
        event["source-ip"] = self.decode_ip(event["source-ip.raw"])
        event["destination-ip"] = self.decode_ip(event["destination-ip.raw"])

        # Check for remaining data, the appid
        remainder = buf[self.fixed_len:]
        if remainder:
            event["appid"] = str(remainder).split("\x00")[0]
        
        return Event(event)

    def decode_ip(self, addr):
        # ipv4
        if len(addr) == 4:
            return socket.inet_ntoa(addr)
        else:
            # ipv6
            parts = struct.unpack(">" + "H"*int(len(addr)/2), addr)
            return ":".join("%04x" % p for p in parts) 


# Map of decoders keyed by record type.
DECODERS = {
    EVENT:          EventDecoder(EVENT_FIELDS),
    EVENT_IP6:      EventDecoder(EVENT_IP6_FIELDS),
    EVENT_V2:       EventDecoder(EVENT_V2_FIELDS),
    EVENT_V2_IP6:   EventDecoder(EVENT_V2_IP6_FIELDS),
}


def decode_record(record_type, buf):
    """Decodes a raw record into an object representing the record.

    :param record_type: The type of record.
    :param buf: Buffer containing the raw record.

    :returns: The decoded record as a :class:'.Event', :class:'.Packet',
    :class:'.ExtraData' or :class:'.Unknown' if the record is of an 
    unknown type.
    """
    if record_type in DECODERS:
        return DECODERS[record_type].decode(buf)
    else:
        return Unknown(record_type, buf)    


def read_record(fileobj):
    """Reads a unified2 record from the provided file object.

    :param fileobj: The file-like object to read from. Currently 
    this object needs to support read, seek and sell.

    :returns: If a complete record is read a :class:'.Record' will 
    be returned, otherwise None will be returned

    If some data is read, but not enought for a whole record, the location 
    of the file object will be reset and a :exc:'.EOFError' exception will
    be raised.
    
    """
    offset = fileobj.tell()
    try:
        buf = fileobj.read(HDR_LEN)
        if not buf:
            #EOF
            return None
        elif len(buf) < HDR_LEN:
            raise EOFError()
        rtype, rlen = struct.unpack(">LL", buf)
        if rtype not in RECORD_TYPES:
            raise UnknownRecordType(rtype)
        buf = fileobj.read(rlen)
        if len(buf) < rlen:
            raise EOFError()
        try:
            return decode_record(rtype, buf)    
        except Exception as err:
            LOG.error("Failed to decode record of type %d (len=%d): %s" % (rtype, rlen, err))
            raise err
    except EOFError as err:
        fileobj.seek(offset)
        raise err


class RecordReader(object):
    """RecordReader reads and decodes unified2 records from a file-like object
    
    :param fileobj: The file-like object to read from
    
    Example::
        fileobj = open("/var/log/snort/snort.alert.xxxxxxxxxx", "rb")
        reader = RecordReader(fileobj)
        for record in reader:
            print(record)
    
    """
    def __init__(self, fileobj):
        self.fileobj = fileobj
    
    def next(self):
        """Return the next record or None if EOF.
        
        Records returned will be one of the types:class: '.Event', 
        :class:'.Unknown' if the record is of an unknown type
        """
        return read_record(self.fileobj)

    def tell(self):
        """Get the current offset in the underlying file object."""
        return self.fileobj.tell()

    def __iter__(self):
        """self.next callable object is called with no arguments for 
        each call to its __next__() method; if the value returned is equal 
        to None, StopIteration will be raised, otherwise the value will be
        returned"""
        return iter(self.next, None)


class SpoolRecordReader(object):
    """SpoolRecordReader reads and decodes records from a unified2 spool directory.
    
    Required parameters:
    :param directory: Path to unified2 spool directory.
    :param prefix: Filename prefix for unified2 log files.
    
    Optional parameters:
    :param init_filename: Filename open on initialization.
    :param init_offset: Offset to seek to on initialization.

    :param follow: Set to true if reading should wait for the next record to become available.

    :param rollover_hook: Function to call on rollover of log file, the first parameter being the filename being closed, the second being the filename being opened.

    Example with following and rollover deletion::
        
        def rollover_hook(closed, opened):
            os.unlink(closed)

        reader = unified2.SpoolRecordReader("/var/log/snort", "unified2.log", rollover_func = rollover_hook,
        	follow = True)

        for record in reader:
            print(record)

"""
    def __init__(self, directory, prefix, init_filename=None, init_offset=None, follow = False, rollover_hook=None):
        self.directory = directory
        self.prefix = prefix
        self.follow = follow
        self.rollover_hook = rollover_hook

        self.fileobj = None
        self.reader = None
        self.fnfilter = "%s*" %(self.prefix)

        if init_filename:
            if os.path.exisits("%s/%s" % (self.directory, os.path.basename(init_filename))):
                self.open_file = (init_filename)
                self.fileobj.seek(init_offset)
                self.reader = RecordReader(self.fileobj)

    def get_filenames(self):
        """Return the filenames (sorted) from the spool directory"""
        return sorted(fnmatch.filter(os.listdir(self.directory), self.fnfilter))

    def open_file(self, filename):
        if self.fileobj:
            closed_filename = self.fileobj.name
            self.fileobj.close()
            LOG.debug("Closed %s.", closed_filename)

        else:
            closed_filename = None

        self.fileobj = open(os.path.join(self.directory, os.path.basename(filename)), 'rb')
        LOG.debug("Opened %s.", self.fileobj.name)
        self.reader = RecordReader(self.fileobj)
        if self.rollover_hook and closed_filename:
            self.rollover_hook(closed_filename, self.fileobj.name)

    def open_next(self):
        """Open the next available file. If a new file is opened its filename will be
        returned, otherwise None will be returned."""
        filenames = self.get_filenames()

        # If there are no files, just return
        if not filenames:
            return

        # If we do not have a current fileobj, open the first file.
        if not self.fileobj:
            self.open_file(filenames[0])
            return os.path.basename(self.fileobj.name)

        if os.path.basename(self.fileobj.name) not in filenames:
            # The current file doesn't exist anymore, move on.
            self.open_file(filenames[0])
            return os.path.basename(self.fileobj.name)
        else:
            current_idx = filenames.index(os.path.basename(self.fileobj.name))
            if current_idx + 1 < len(filenames):
                self.fileobj.close()
                self.open_file(filenames[current_idx + 1])
                return os.path.basename(self.fileobj.name)

    def tell(self):
        """Return a tuple containing the filename and offset of the file
        currently being processed."""
        if self.fileobj:
            return (self.fileobj.name, self.fileobj.tell())
        return None, None

    def next(self):
        """Return the next decoded unified2 record from the spool
        directory.
        """
        # If we don't have a current file, try to open one. Failing
        # that just return
        if self.fileobj == None:
            if not self.open_next():
                return

        # Now try to get a record. If we can't see if there is a 
        # new file and try again.
        try:
            record = self.reader.next()
        except EOFError:
            return

        if record:
            return record
        else:
            while True:
                if self.open_next():
                    try:
                        record = self.reader.next()
                    except EOFError:
                        return
                    if record:
                        return record
                else:
                    return None

    def iter_next(self):
        """Return the next record or None if EOF.
        
        If in following mode and EOF, this method will sleep
        and try again.

        :returns: A record of type :class:'.Event', :class:'.Packet',
        :class:'.ExtraData or :class:'.Unknown' if the record is of 
        an unknown type.

        """
        while True:
            record = self.next()
            if record:
                return record
            if not self.follow:
                return
            else:
                # Sleep for a moment and try again
                time.sleep(0.01)

    def __iter__(self):
        return iter(self.iter_next, None)

