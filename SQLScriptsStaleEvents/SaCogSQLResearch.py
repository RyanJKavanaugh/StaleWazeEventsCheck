import pyodbc
import json
import requests
import os
import sys
from StringIO import StringIO

# To do: set up delete function, figure out which crashes need to be deleted
# SERVER CREDENTIALS
# server ='sasql'
server = 'SQLSTAGE1, 1432'
database ='sacars'
username ='sacars'
password ='sacars'

# CONNECT TO THE SERVER VIA THE ABOVE CREDENTIALS
conn = pyodbc.connect("DRIVER={SQL Server};SERVER=" + server + ";UID=" + username + ";PWD=" + password + ";DATABASE=" + database)
cursor = conn.cursor()

# ENTER SQL STATEMENT HERE
# All save for 2:21 and 2:22
# cursor.execute('SELECT * FROM [SACARS].[dbo].[evt_Situations] WHERE update_timestamp < DATEADD(hh, -11, GETDATE()) AND (situation_update_json LIKE \'%"headline":{"category":2,"code":13%}%\' OR situation_update_json LIKE \'%"headline":{"category":2,"code":14%}%\')'
#                ' AND (situation_update_json NOT LIKE \'%"headline":{"category":2,"code":129}%\')') # AND update_timestamp < DATEADD(hh, -1, GETDATE())')

# Get only the most recent event update

cursor.execute('SELECT sub.* FROM(SELECT situation_id, update_number, update_timestamp, situation_update_json FROM (SELECT *, maxnum = MAX(update_number) OVER (PARTITION BY situation_id) FROM [SACARS].[dbo].[evt_Situations]) as s WHERE update_number = maxnum) sub WHERE situation_update_json LIKE \'%"headline":{\"category\":2,\"code\":1}%\' AND update_timestamp < DATEADD(hh, -11, GETDATE()) AND situation_update_json NOT LIKE \'%DELETE%\'')

# # USED FOR EXECUTINGS A DELETE STATEMENT
# conn.commit()

# FETCH ALL DATA FROM THE SQL QUERY AND PRINT IT
allEventsJson = cursor.fetchall()

# Number of relevant events in the database for testing purposes
numberOfEvents = len(allEventsJson)
print '\n' + 'Events In The Database: ' + str(numberOfEvents)

# List to hold IDs of every relevant crash event (i.e. older than 8 hours and part of most recent even ID update)
crashEventIDs = []

# Add all IDs from the SQL database JSON to list 'crashEventsIDs'
for item in allEventsJson:
        crashEventIDs.append(item[0])

print 'The number of items in Crash Events IDs: ' + str(len(crashEventIDs))

deleteCounter = 0
itemsInIDList = len(crashEventIDs)


# # Deletes first item in ID list
# url = 'http://cramgmt.carsprogram.int/deleteEvent/deleteEvent.php?platform=Staging&state=SACOG&eID=' + str(crashEventIDs[0]) + '&mode=Delete'
# print url
# r = requests.get(url)
# print r.status_code

# # Deletes events in loop
# for id in crashEventIDs:
#     if deleteCounter < itemsInIDList:
#         url = 'http://cramgmt.carsprogram.int/deleteEvent/deleteEvent.php?platform=Staging&state=SACOG&eID=' + str(crashEventIDs[deleteCounter]) + '&mode=Delete'
#         print url
#         r = requests.get(url)
#         print r.status_code
#         #deleteCounter += 1