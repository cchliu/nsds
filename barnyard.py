"""Create an alert database and insert alerts into it.

Alerts are from the snort.alert unified2 files.

::
    usage:
"""
import sqlite3
import logging
import unified2
import sys

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Extract out TCP alerts
TCP_PROTOCOL = 6

# Fields in an EVENT record
EVENT_FIELDS = [
    'sensor-id INTEGER',
    'event-id INTEGER',
    'event-second INTEGER',
    'event-microsecond INTEGER',
    'signature-id INTEGER',
    'generator-id INTEGER',
    'signature-revision INTEGER',
    'classification-id INTEGER',
    'priority INTEGER',
    'source-ip TEXT',
    'destination-ip TEXT',
    'sport-itype INTEGER',
    'dport-icode INTEGER',
    'protocol INTEGER',
    'impact-flag INTEGER',
    'impact INTEGER',
    'blocked INTEGER',
    'mpls-label INTEGER',
    'vlan-id INTEGER',
    'pad2 INTEGER'
]
     

def create_table(conn, table_name):
    """Create the alert table.

    :param conn: The sqlite connection.
    :param table_name: The name of the table to be created.

    """
    # Create the table
    c = conn.cursor()
    _columns = ','.join(EVENT_FIELDS)
    _columns = _columns.replace('-', '_')
    create_query = "CREATE TABLE IF NOT EXISTS %s (%s)" % (table_name, _columns)
    LOG.info(create_query) 
    c.execute(create_query)

    # Commit changes
    conn.commit()


def insert_alerts(conn, table_name, chunk):
    """Insert alerts to the database.

    :param conn: The sqlite connection
    :param table_name: The name of the table to insert alerts to.
    :param chunk: A chunk of records to be inserted.

    """
    c = conn.cursor()
    _insert_tmpl = "INSERT INTO %s VALUES (%s)" % (table_name, ','.join(['?']*len(EVENT_FIELDS)))

    c.execute('BEGIN TRANSACTION')
    for row in chunk:
        try:
            c.execute(_insert_tmpl, row)
        except Exception as e:
            LOG.error("Failed to insert on line %s: %s" % (','.join([str(i) for i in row]), e))
    conn.commit()


def read_alerts(conn, table_name):
    """Read alerts from unified2 files.
    
    :param conn: The sqlite connection.
    :param table_name: The name of the table to insert alerts to.

    Divide the alert data into 1000 rows each and commit data in chunks.
    """
    fileobj = open("Alert/snort.alert.1496476621", 'rb')
    reader = unified2.RecordReader(fileobj)

    chunk = []
    for record in reader:
        row = []
        for field in EVENT_FIELDS:
            field_name = field.split(' ')[0]
            row.append(record[field_name])
        if record['protocol'] == TCP_PROTOCOL:
            chunk.append(row)
        if len(chunk) % 1000 == 0:
            insert_alerts(conn, table_name, chunk)
            chunk = []
    if chunk:
        insert_alerts(conn, table_name, chunk)
        chunk = [] 

     
def main():
    sqlite_file = 'alert.sqlite'
    # Connecting to the database file
    conn = sqlite3.connect(sqlite_file)

    table_name = 'ALERT'
    create_table(conn, table_name)

    read_alerts(conn, table_name)

if __name__ == "__main__":
    main() 
