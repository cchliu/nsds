"""Load filtered flows into a database."""
import sys
import logging
import sqlite3

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def create_table(conn, table_name):
    """Create a table to hold packet records.

    :param conn: The database connection.
    :param table_name: The name of the table to be created.

    :returns: A datatype cast specifying the datatype of each column.

    """
    datatype = {
        "TEXT":str,
        "INTEGER":int,
        "REAL":float
    }

    _cast = []

    _columns = []
    csv_fields_file = "fields_convertedtocsv.txt"
    with open(csv_fields_file, 'rb') as ff:
        for line in ff:
            # Ignore the comment line
            if len(line)>0 and line[0] != '#':
                field, ftype = line.rstrip('\n').split(',')
                _columns.append('%s %s' % (field.replace('.', '_'), ftype))
                _cast.append(datatype[ftype])

    _columns = ','.join(_columns)
    _query = "CREATE TABLE IF NOT EXISTS %s (%s)" % (table_name, _columns)
    c = conn.cursor()
    LOG.debug("sqlite command to create TRACE table: %s" % (_query))
    c.execute(_query)
    # Committing changes
    conn.commit()
    return _cast


def chunks(data, rows=10000):
    """Divides the data into 10000 rows each."""
    for i in xrange(0, len(data), rows):
        yield data[i:i+rows]


def insert_packets(records, _cast, conn, table_name):
    """Insert packet records into the database in chunks.

    :param records: A list of packet records to load into the table.
    :param _cast: A list of datatypes for type convertion.
    :param conn: The database connection.

    """  
    data = []
    for record in records:
        record = record.split('\t')
        values = [_cast[idx](k) for idx, k in enumerate(record)]
        data.append(values)

    divData = chunks(data)
    _insert_tmpl = 'INSERT INTO %s VALUES (%s)' % (table_name, ','.join(['?']*len(data[0])))
    c = conn.cursor()
    for chunk in divData:
        c.execute('BEGIN TRANSACTION')
        for row in chunk:
            try:
                c.execute(_insert_tmpl, row)
            except Exception as e:
                LOG.error("Error on line %s: %s" % (row, e))
        conn.commit()
