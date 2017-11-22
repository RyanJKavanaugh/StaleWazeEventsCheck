# coding=utf-8
import json
import requests
import datetime
import time
from email.mime.text import MIMEText
import smtplib
# -*- coding: utf-8 -*-

# This is for IA

urlWazeImporter = 'http://ia.carsstage.org/waze_v1/api/wazeEvents'

jsonImporterDataIA = json.loads(requests.get(urlWazeImporter).content)

counterOne = 0
counter = 0
wazeEventsWithIDAndUUID = {}

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


def deleteStaleEvents(allStaleWazeAlertIDs):
    for WazeAlertID in allStaleWazeAlertIDs:
        url = 'http://cramgmt.carsprogram.int/deleteEvent/deleteEvent.php?platform=Staging&state=Iowa&eID=' + str(WazeAlertID) + '&mode=Delete'
        r = requests.get(url)
        if r.status_code != 200:
            print WazeAlertID
            print r.status_code

# GET THE IMPORT DATA

for wazeEvent in jsonImporterDataIA:
    tempArray = []
    situationID = wazeEvent['situationIdentifier']
    jsonObject = wazeEvent['wazeAlerts']

    if len(jsonObject) > 1:

        for jsonItem in jsonObject:
            uuIDtemp = jsonItem['uuid']

            tempArray.append(uuIDtemp)
    else:
        uuID = wazeEvent['wazeAlerts'][0]['uuid']
        tempArray.append(uuID)

    wazeEventsWithIDAndUUID[situationID] = tempArray


# GET THE FEED DATA

urlWazeFeed = 'https://na-georss.waze.com/rtserver/web/TGeoRSS?tk=ccp_partner&ccp_partner_name=Iowa&muao=false&fa=false&polygon=-96.921387,43.628123;-90.922852,43.628123;-90.791016,42.851806;-89.956055,42.032974;-90.411987,41.327326;-91.340332,40.262761;-95.976563,40.446947;-95.993042,41.450961;-96.278687,41.611335;-96.679688,42.734909;-96.921387,43.628123;-96.921387,43.628123&format=JSON&types=traffic,alerts,irregularities'
jsonFeedDataIA = json.loads(requests.get(urlWazeFeed).content)

#TODO: ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? Do I need more than 'alerts' ? ? ? ? ? ? ? ? ? ? ? ? ? ? ? ?

uuIDFeedList = []
lengthOflist = len(jsonFeedDataIA['alerts'])

# Get list of uuIDs from the Waze Feed Json

for x in range(0, lengthOflist):
    uuIDFeedNumber = jsonFeedDataIA['alerts'][x]['uuid']
    uuIDFeedList.append(uuIDFeedNumber)

emailString = ''

# COMPARE THE TWO
itemCount = 1
allStaleWazeAlertIDs = []

emailString = 'Hello,' + '\n' + '\n' + 'The following WazeAlerts IDs are in the importer feed, but not in the accurate feed: ' + '\n' + '\n'

for IDImporter in wazeEventsWithIDAndUUID:
    correct = False

    # Grab the uuID number, I.E. the long id number
    uuIDImporter = wazeEventsWithIDAndUUID[IDImporter]

    # Determine how many items are in the list
    numberOfItems = len(uuIDImporter)

    # If there is more than one item then run through each item and see if atleast one matches, if so then ignore this item
    if numberOfItems > 1:

        # Create a for loop that runs through each item in the list
        for itemNumber in range(0, numberOfItems):
            # If the uuID number is not in the feed data then we need to pay attention to it
            if uuIDImporter[itemNumber] in uuIDFeedList:
                correct = True
                break

        if not correct:
            print str(itemCount) + '. ' + "This WazeAlert Is Missing From The Feed And Has Multiple uuIDs:"
            print '   ID: ' + IDImporter
            print '   UU ID: ' + uuIDImporter[itemNumber] #TODO: print all IDs
            print
            emailString = emailString + str(itemCount) + '. ' + 'ID: ' + IDImporter + '\n'
            emailString = emailString + 'UU ID: ' + uuIDImporter[0] + '\n' + '\n'
            itemCount += 1
            allStaleWazeAlertIDs.append(IDImporter)

    # If there is only one item then just check the first item in the list
    else:
        if uuIDImporter[0] not in uuIDFeedList:
            print str(itemCount) + '. ' + 'This WazeAlert Is Missing From Feed and Has a Single uuID:'
            print '   ID: ' + IDImporter
            print '   UU ID: ' + uuIDImporter[0]
            print
            emailString = emailString + str(itemCount) + '. ' + 'ID: ' + IDImporter + '\n'
            emailString = emailString + 'UU ID: ' + uuIDImporter[0] + '\n' + '\n'
            itemCount += 1
            allStaleWazeAlertIDs.append(IDImporter)

emailString = emailString + '\n' + 'All the best,' + '\n' + '\n' + 'Castle Rock DevOps/QA Robot'

print emailString

if itemCount > 0:
    sender = 'ryan.kavanaugh@crc-corp.com'
    receiver = 'ryan.kavanaugh@crc-corp.com'
    #receiver = ['ryan.kavanaugh@crc-corp.com', 'aaron.billington@crc-corp.com']
    subject = 'Stale WazeAlerts'
    message = emailString


sendEmail(sender, receiver, subject, message)

deleteStaleEvents(allStaleWazeAlertIDs)
