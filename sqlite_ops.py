# Import sqlite3 module into
# this program as sq
from modulefinder import AddPackagePath
import sqlite3 as sq
from sqlite3 import Error
import warnings


# Import pandas module into
# this program as pd
import pandas as pd
import aflog
logger = aflog.logging.getLogger(__name__)


def create_connection(db_file):
    """[Creates a SQLite database connection]

    Args:
        db_file ([str]): [database file name]
    """
    conn = None
    try:
        conn = sq.connect(db_file)
    except Error as e:
        print(e)
    return conn
	
def create_cherwell_table(connection, csv_data):  
	'''
	At this time I do not have api access to query
	the cherwell cmdb directly, so the application
	relies on a csv import to load a local db file
	file data to support the cmdb search.

	This function requires a db connetion and 
	the name of the csv file to import.  

	'''
	
	# Create a cursor object
	curs = connection.cursor()
	
	# Run create table sql query
	curs.execute("CREATE TABLE IF NOT EXISTS cw_computers" +
		"(Manufacturer	TEXT, Model TEXT, SerialNumber TEXT," +
		"AssetTag INTEGER, Status TEXT, FriendlyName TEXT," +
		"LastModifiedDateTime TEXT, ComputerType TEXT," +
		"Condition	TEXT, CreatedBy	TEXT, CreatedDateTime	TEXT," +
		"'EFI/BIOSPassword'	TEXT, IPAddress	TEXT, LocationID TEXT," +
		"Note TEXT, SiteCode TEXT, SiteName TEXT, SSD	TEXT," +
		"FullName TEXT, UserName	TEXT, Version	TEXT," +
		"OperatingSystem	TEXT, OperatingSystemFamily	TEXT," +
		"Email	TEXT)")

	
	# Load CSV data into Pandas DataFrame
	cw_data = pd.read_csv(csv_data)
	logger.info('Imported(rows,cols)=({},{}) from {}'.format(cw_data.shape[0],cw_data.shape[1], csv_data))
	cw_data.columns = cw_data.columns.str.replace(' ', '')
	# Write the data to a sqlite db table
	cw_data.to_sql('cw_computers', connection, if_exists='replace', index=False)
	
	#----------------------
	curs.execute("CREATE TABLE IF NOT EXISTS datetime_int (d1 int)")
	curs.execute("DELETE from datetime_int ") #clear table - only want one record
	curs.execute("INSERT INTO datetime_int (d1) VALUES(strftime('%s','now'))")
	curs.execute("SELECT datetime(d1,'unixepoch')FROM datetime_int")
	rows = curs.fetchall()
	logger.info(rows)

	connection.commit()

def get_refresh_time(connection):
	# Create a cursor object
	curs = connection.cursor()
	try:
		curs.execute("SELECT datetime(d1,'unixepoch', 'localtime')FROM datetime_int")
		rows = curs.fetchall()
		logger.info(rows)
		return rows[0][0]
	except: 
		return 'Unknown!  Please refresh DB!'


def select_all_records(conn):
    """
    Query all rows in the table
    :param conn: the Connection object
    :return nothing - used fot test only:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM cw_computers")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def select_all_cw_by_email(conn, email):
	"""
	Query all rows in the table
	matching email passed in Email Col
	:returns matching rows:
	"""
	cur = conn.cursor()
	cur.execute("SELECT Model, SerialNumber, AssetTag FROM cw_computers WHERE Email=?", (email,))
	rows = cur.fetchall()
	logger.info('CW query returned {} rows.'.format(len(rows)))
	return rows

def main():
	#test files in dev env
	db_file = '/Users/dinorusso/PyDev/AssetFinderv4/data/test.db'
	csv_file = '/Users/dinorusso/PyDev/AssetFinderv4/data/cherwell_computers.csv'
	load_csv = True #change to true to test updating the table

	#connect to db
	connection = create_connection(db_file)
	warnings.filterwarnings("ignore")
	
	if load_csv:
		create_cherwell_table(connection, csv_file)

	#select_all_records(connection)
        
	email_address = input('\nEnter email address:')
	print('Cherwell:')
	rows=select_all_cw_by_email(connection, email_address)
	for row in rows:
		print(row)

	print(get_refresh_time(connection))

    
if __name__ == '__main__':
    main()