import pyodbc
import json
import requests
import os
import sys
import smtplib
import datetime
import time
from email.mime.text import MIMEText
from StringIO import StringIO


# SERVER CREDENTIALS
server = 'SQLSTAGE1, 1432'
database ='iacars'
username ='iacars'
password ='iacars'

# CONNECT TO THE SERVER VIA THE ABOVE CREDENTIALS
conn = pyodbc.connect("DRIVER={SQL Server};SERVER=" + server + ";UID=" + username + ";PWD=" + password + ";DATABASE=" + database)
cursor = conn.cursor()

def sendEmail(fromm, to, subject, message):
    # message = """From: {} To: {} Subject: {} {}""".format(fromm, to, subject, message)

    today = str(time.strftime("%m-%d-%y"))

    try:
        smtpObj = smtplib.SMTP('10.10.2.247')
        smtpObj.set_debuglevel(1)
        msg = MIMEText(message)
        sender = fromm
        receivers = to
        msg['Subject'] = "Stale WazeAlerts | " + today
        msg['From'] = sender
        smtpObj.sendmail(sender, receivers, msg.as_string())

        print "Successfully sent email: {}".format(subject)
    except Exception, e:
        print e
        print "Error: unable to send email"



# ENTER SQL STATEMENT HERE
cursor.execute('SELECT * FROM [IACARS].[dbo].[evt_Situations] WHERE update_timestamp < DATEADD(hh, -15, GETDATE()) '
               'AND (situation_namespace LIKE \'%WazeAlerts%\') '
               'AND situation_update_json NOT LIKE \'%"headline":{"category":46,"code":28%\''
               'AND situation_update_json NOT LIKE \'%"headline":{"category":46,"code":30%\''
               'AND situation_update_json NOT LIKE \'%"headline":{"category":46,"code":59%\''
               'AND situation_update_json NOT LIKE \'%"headline":{"category":46,"code":61%\'')

wazeJson = cursor.fetchall()
print len(wazeJson)

# check against the API with all these things. Schedule it once a day. http://ia.carsstage.org/waze_v1/
apilink = 'http://ia.carsstage.org:80/waze_v1/api/wazeEvents/'
emailString = ''
lineCounter = 1

if len(wazeJson) > 0:
    emailString = 'Hello,' + '\n' + '\n' + 'The following WazeAlerts IDs are older than 8 hours, have been checked against the API, and are unrelated to construction: ' + '\n' + '\n'
    # Go through all Waze Events
    for item in wazeJson:
        link = apilink + str(item[1])
        r = requests.get(link)
        # If the API request is not healthy (I.E. if the Waze ID is not supposed to be on the map), then email it to us.
        if r.status_code != 200:
            emailString = emailString + str(lineCounter) + '. ' + str(item[1]) + '\n'
            emailString = emailString + 'API link: ' + link + ': ' + str(r.status_code) + '\n' + '\n'
            lineCounter += 1
    emailString = emailString + '\n' + 'Best regards,' + '\n' + '\n' + 'Castle Rock QA Robot'

print emailString


if emailString != '':
    Message = emailString
    Subject = 'Test Email'
    From = 'ryan.kavanaugh@crc-corp.com'
    To = 'ryan.kavanaugh@crc-corp.com'
    #To = ['ryan.kavanaugh@crc-corp.com', 'mary.crowe@crc-corp.com', 'aaron.billington@crc-corp.com']
    print emailString
    sendEmail(From, To, Subject, Message)


# # Deletes first item in ID list
# url = 'http://cramgmt.carsprogram.int/deleteEvent/deleteEvent.php?platform=Staging&state=SACOG&eID=' + str(WazeID) + '&mode=Delete'
# print url
# r = requests.get(url)
# print r.status_code