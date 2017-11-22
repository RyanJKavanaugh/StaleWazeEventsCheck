# coding=utf-8
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import unittest
import json
import requests
import xlrd
from pyvirtualdisplay import Display
# -*- coding: utf-8 -*-


def post_new_place(placeJson, authToken):
    apiUrl = 'http://latg.carsprogram.org:80/publicaccounts_v1/api/accounts/15466/customAreas?authTokenId=' + str(authToken)
    newPlacePost = requests.post(apiUrl, json=placeJson)

    data = json.loads(newPlacePost.content)
    id = data.get('id')
    return id


def delete_place(placeID, authToken):
    deleteUrl = 'https://hb.511la.org/tgpublicaccounts/api/accounts/15466/customAreas/' + str(placeID) + '?authTokenId=' + str(authToken)
    deleteItem = requests.delete(deleteUrl)


class Verify_Login(unittest.TestCase):


    def setUp(self):
        self.driver = webdriver.Chrome()


    def test_login(self):
        userInfo = {"userId":"ryan.kavanaugh@crc-corp.com","password":"test"}
        authTokenURL = 'http://latg.carsprogram.org:80/publicaccounts_v1/api/authTokens'

        myResponse = requests.post(authTokenURL, json=userInfo)
        jData = json.loads(myResponse.content)
        authToken = jData.get('id')
        accountID = jData.get('accountId')

        # This section gets the user's current saved places
        #       This allows us to create places and make sure they hit the api & that we can create stuff via the API
        #       and then check to see that the saved places showed up on the TG-Web site

        customAreasAPIUrl = 'http://latg.carsprogram.org:80/publicaccounts_v1/api/accounts/' + str(accountID) + '/customAreas?authTokenId=' + str(authToken)
        customAreaJson = requests.get(customAreasAPIUrl)

        data = customAreaJson.json()

        if len(data) > 0:
            print data[0].get('name')

        # Json for different places for testing saved 'favorite places'
        newPlace = {"accountId":15466,"name":"Elton","normalDuration":None,"polygon":{"type":"Polygon","coordinates":[[[-93.80519524960937,30.253889283839378],[-93.80519524960937,30.70835019075345],[-91.58870355039062,30.70835019075345],[-91.58870355039062,30.253889283839378],[-93.80519524960937,30.253889283839378]]]},"bounds":None,"customAreaShapeSource":"CONFIG_DEFINED","embedded":{},"id":None}
        newPlace2 = {"accountId":15466,"name":"Louisiana","normalDuration":None,"polygon":{"type":"Polygon","coordinates":[[[-107.364004765625,27.5582840804247],[-107.364004765625,34.244808909713534],[-75.437735234375,34.244808909713534],[-75.437735234375,27.5582840804247],[-107.364004765625,27.5582840804247]]]},"bounds":None,"customAreaShapeSource":"CONFIG_DEFINED","embedded":{},"id":None}
        newPlace3 = {"accountId":15466,"name":"Baton Rouge","normalDuration":None,"polygon":{"type":"Polygon","coordinates":[[[-92.21211129902338,30.231198967440722],[-92.21211129902338,30.651510408818112],[-90.0107258009765,30.651510408818112],[-90.0107258009765,30.231198967440722],[-92.21211129902338,30.231198967440722]]]},"bounds":None,"customAreaShapeSource":"CONFIG_DEFINED","embedded":{},"id":None}

        # Places IDs
        id1 = post_new_place(newPlace, authToken)
        id2 = post_new_place(newPlace2, authToken)
        id3 = post_new_place(newPlace3, authToken)

        # Logon to TG-Web
        driver = self.driver
        driver.get('https://hb.511la.org/#favorites?layers=roadReports%2Ccameras&timeFrame=TODAY')
        loginElement = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'userAccountEmail')))
        driver.find_element_by_id('userAccountEmail').send_keys('ryan.kavanaugh@crc-corp.com')
        driver.find_element_by_id('userAccountPassword').send_keys('test')
        driver.find_element_by_id('userAccountPassword').submit()

        # Head to the favorites page
        pageLoadWait = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, 'favoriteBtn')))
        time.sleep(2)
        signInButton = driver.find_element_by_id('favoriteBtn')
        signInButton.click()

        time.sleep(6)

        allFavoritesPlaces = driver.find_elements_by_class_name('user-favorite-item')

        Elton = False
        Lou = False
        BatonRouge = False

        for favorite in allFavoritesPlaces:
            print favorite.text
            favoritesWithAPIInfo = favorite.text
            if 'Elton' in favoritesWithAPIInfo:
                Elton = True
            if 'Louisiana' in favoritesWithAPIInfo:
                Lou = True
            if 'Baton Rouge' in favoritesWithAPIInfo:
                BatonRouge = True

        time.sleep(3)

        delete_place(id1, authToken)
        delete_place(id2, authToken)
        delete_place(id3, authToken)

        # Here we test that the favorite places correctly populated TG-Web
        assert Elton
        assert Lou
        assert BatonRouge


    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()