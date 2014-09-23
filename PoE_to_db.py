'''
Created on Sep 16, 2014

@author: leila

PoE meter - query parameters to database
----------------------------------------------
reads the PoE meter data through http connection and passes them to MySQL database
- make sure to have MySQL installed; if not already, then
- execute sudo apt-get install mysql-server mysql-client
- provide a database named flm (or alter below code accordingly)
- for convenient access in Python2 (sic!) install the MySQLdb module
- with sudo apt-get install python-mysqldb
- for convenient http-communication install httplib2
- for that please refer to http://code.google.com/p/httplib2/
- before running this code make sure you have created a database named PoE on the root account of your MySQL server
- or change the values in line 101 - 110 according to your database properties
'''

__author__ = "Leil Sharifi"
__copyright__ = "September 2014"
__credits__ = ["raspberrypi.org", "httplib2", "Simon Monk"]


# now the code
# import http support
import httplib2, httplib
#import urllib2
# import database support
import MySQLdb
# import relevant system functions
import time, sys
from datetime import datetime
# for socket.error (occurred on FLM update -> connection refused)
import socket
# prepare logging to see what happens in the background
import logging, warnings
# import signal handling for external kill command
import signal

# now define used functions
# routine to handle errors
def handleError(e):
    logging.error('Error %d: %s' % (e.args[0], e.args[1]))
    sys.exit (1)

# routine to properly end a job
def killHandler(signum, stackframe):
    if db.open:
        db.close()
    logging.info('Job ended')
    sys.exit(0)



def parse_content(content):
    lines = content.split("\n")
    print lines
    print "\n" 
    parsed_content = []
    final_content = []    
    stripped_content = lines[10:-3]    
    for i in xrange(0,len(stripped_content)):
        if i%2 ==0:
            parsed_content.append(stripped_content[i])
    print parsed_content, "\n"

    for element in parsed_content:
        element = element.strip("<br>\r")
        strip = element.split(",")
        temp_list=[]        
        for stripped in strip:
            temp_list.append(stripped.split("=")[1])
        
        final_content.append(temp_list)    
    
    print final_content    
    return final_content     


# initialize output options
logging.basicConfig(filename='PoE_query.log',
                    level = logging.ERROR, #level=logging.DEBUG,
                    filemode='a',
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S')
logging.captureWarnings(True)
# ignore warnings, e.g. that table flmdata exists...
warnings.filterwarnings('ignore')

# handle a kill signal to make an educated end on "kill <pid>"
signal.signal(signal.SIGTERM, killHandler)
# handle Ctrl-C in online mode
signal.signal(signal.SIGINT, killHandler)


# define your local PoE's url here,
# for IP address query your DHCP server or use the fixed IP address you assigned
url = 'http://10.1.24.99/'
# define local query (Sampling rate per minute)
query = '?setS=1'

# connect to database
try:
    db = MySQLdb.connect(host='localhost',    # whereever you located your db
                         user='root',         # use your convenient user
                         passwd='raspberry',  # and password
                         db='PoE')            # and database
except MySQLdb.Error, e:
    handleError(e)

# prepare table to write data into
# create a table to store FLM values (if it does not exist)
try:
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS poedata
        (
            v1    CHAR(10),
        i1      CHAR(10),
            power1     CHAR(10),
        v2      CHAR(10),
        i2      CHAR(10),
        power2     CHAR(10),
        temp       CHAR(10),
        timestamp TIMESTAMP, 
            UNIQUE KEY (timestamp)
        )
        """)
except MySQLdb.Error, e:
    handleError(e)
    
# prepare querying data from local FLM
PoE = httplib2.Http()
while True:
# query the sensors
    #for sensor, senid in sensors:
    req = url+query
    print req        
    headers = {'Accept':'application/json' }
    # try until fetched a valid JSON result
    error = True
    while error:
        error = False
        try:
            response, content = PoE.request(req, 'GET', headers=headers)   
            content=parse_content(content) 
        except (httplib2.HttpLib2Error, httplib.IncompleteRead, socket.error):
            error = True
            logging.error('Connection error occurred')
        if response.status == 200:
            try:
                data = content
                print data
                logging.info(content)
            except ValueError:
                error = True
                # it is also an error if there is no JSON content
                if data == 0:
                    error = True
                else:
                    error = True
# save sensor data in database
    for element in data:
        print element
        i1, v1, power1, i2, v2, power2, temp = element
        try:
            if i1 == 'nan':
                i1 = 0
            if v1 == 'nan':
                v1 = 0
            if power1 == 'nan':
                power1 = 0
            if i2 == 'nan':
                i2 = 0
            if v2 == 'nan':
                v2 = 0
            if power2 == 'nan':
                power2 = 0
            if temp == 'nan':
                temp = 0
            timestamp = datetime.now()
            print "timestamp = " , timestamp
            # save values to database so that they occur only once each
            # for that update already read sensor data within the last
            # 30 seconds
            cur.execute("""INSERT INTO poedata (v1, i1, power1, v2, i2, power2, temp, timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                v1 = VALUES(v1),
                i1 = VALUES(i1),
                power1 = VALUES(power1),
                v2 = VALUES(v2),
                i2 = VALUES(i2),
                power2 = VALUES(power2),
                temp = VALUES(temp),
                timestamp = VALUES(timestamp)""",
                ( v1, i1, power1, v2, i2, power2, temp, str(timestamp)))
            db.commit()
        except MySQLdb.Error, e:
            handleError(e)
# wait for 60 seconds
    time.sleep(6)
# note - this is done in an infinite loop for now
# this may be removed to run the script via a cron job,
# but cron goes down to 1 min only...
# with the infinite loop start the script to run also after logoff from RPi:
# sudo nohup python PoE_query_to_db.py &
