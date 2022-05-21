import calendar
import datetime
import json
import os
import random
import smtplib
import ssl
import time
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def reserve(campgroundID, siteID, firstDay, days, ground):
    reserveUrl = "https://www.recreation.gov/camping/campgrounds/" + campgroundID + "/availability"
    file_name = 'geckodriver'
    file_name = os.path.join(os.path.dirname(sys.executable), file_name)
    browser = webdriver.Firefox(executable_path=file_name)
    browser.get(reserveUrl)
    time.sleep(1.2)
    dateBox = browser.find_element_by_id("single-date-picker-1")
    dateBox.send_keys(Keys.CONTROL + 'A')
    dateBox.send_keys(firstDay.strftime("%m/%d/%Y"))
    time.sleep(1.2)
    browser.execute_script("arguments[0].scrollIntoView({behavior: \"auto\", block: \"center\", inline: \"nearest\"})", browser.find_element_by_id(siteID))
    time.sleep(0.100)
    browser.find_element_by_id(siteID).find_element_by_class_name("available").click()
    if days > 1:
        dateBox.send_keys(Keys.CONTROL + 'A')
        dateBox.send_keys((firstDay + datetime.timedelta(days=days)).strftime("%m/%d/%Y"))
        time.sleep(1.2)
        browser.execute_script("arguments[0].scrollIntoView({behavior: \"auto\", block: \"center\", inline: \"nearest\"})", browser.find_element_by_id(siteID))
        time.sleep(0.100)
        browser.find_element_by_id(siteID).find_elements_by_tag_name("td")[1].click()
    time.sleep(0.500)
    browser.find_element_by_class_name("sarsa-button.sarsa-button-primary.sarsa-button-md").click()
    browser.find_element_by_id("rec-acct-sign-in-email-address").send_keys(recEmail)
    browser.find_element_by_id("rec-acct-sign-in-password").send_keys(recPass)
    browser.find_element_by_class_name("sarsa-button.rec-acct-sign-in-btn.sarsa-button-primary.sarsa-button-lg.sarsa-button-fit-container").click()
    cont = "Subject:Reservation added to Cart\n\nAttention new reservation added to the cart!\n\nAt Park: " + parentOf[
        ground] + ", at Campsite: " + ground + ".\nStarting from day: " + startDate.strftime("%Y-%m-%d") + " for " + str(days) + " days."
    executor.submit(send_mail, "crootcroot2018@gmail.com", "AHmed12345", cont, email)


def send_mail(mail, password, content, recipient):
    port = 465
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(mail, password)
        server.sendmail("admin@camping_bot.com", recipient, content)


filename = 'campsAreas.json'
filename = os.path.join(os.path.dirname(sys.executable), filename)
executor = ThreadPoolExecutor(5)
delay = [7, 8, 8, 8, 9, 9, 10]
data = open(filename, "r")
campsAreas = dict(json.load(data))
data.close()
filename = 'campGrounds.json'
filename = os.path.join(os.path.dirname(sys.executable), filename)
data = open(filename, "r")
campGrounds = dict(json.load(data))
data.close()
filename = 'user-agents_browser.json'
filename = os.path.join(os.path.dirname(sys.executable), filename)
agents = open(filename, "r")
browserAgents = list(json.load(agents))
agents.close()

places = []
isAll = []
campSites = []
park = ""
campground = ""
parentOf = dict()
campSiteIDOf = []
pre = "https://www.recreation.gov/api/camps/availability/campground/"
base = "https://www.recreation.gov/camping/campgrounds/"

n = int(input("Enter number of parks of interest: "))
for i in range(n):
    park = (input("Enter park #" + str(i + 1) + ": "))
    g = int(input("Enter number of campgrounds of interest in " + park + ": "))
    for j in range(g):
        campground = input("Enter campground #" + str(j + 1) + " for " + park + ": ")
        parentOf[campground] = park
        places.append(campground)
        noCamp = input("Enter number of campsites of interest in " + campground + " :")
        if noCamp == "ALL":
            isAll.append(True)
            s = 0
        else:
            isAll.append(False)
            s = int(noCamp)
        tmpSites = []
        for k in range(s):
            tmpSites.append(input("Enter campsite #" + str(k + 1) + " :"))
        campSites.append(tmpSites)
startDate = datetime.datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d")
endDate = datetime.datetime.strptime(input("Enter end date (YYYY-MM-DD): "), "%Y-%m-%d")

minDays = int(input("Enter minimum number of days: "))
maxDays = int(input("Enter maximum number of days: "))
email = input("Enter your email to receive notifications: ")
recEmail = input("Enter your recreation.gov email: ")
recPass = input("Enter your recreation.gov pass: ")
headersDict = {
    "user-agent": random.choice(browserAgents),
    "authority": "www.recreation.gov",
    "method": "GET",
    "path": "",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    "cache-control": "no-cache, no-store, must-revalidate",
    "pragma": "no-cache",
    "referer": "",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "start_date": ""
}
tmpDate = datetime.datetime(startDate.year, startDate.month, 1)
for i in range(len(places)):
    tmpUrl = campGrounds[places[i]] + "/month?start_date=" + tmpDate.strftime("%Y-%m-%dT%H%%3A%M%%3A%S.000Z")
    url = pre + tmpUrl
    headersDict["referer"] = base + campGrounds[places[i]] + "/availability"
    headersDict["path"] = "/api/camps/availability/campground/" + tmpUrl
    headersDict["start_date"] = tmpDate.strftime("%Y-%m-%dT%H%%3A%M%%3A%S.000Z")
    tmpResponse = json.loads(requests.get(url, headers=headersDict).content.decode("utf-8"))
    headersDict["user-agent"] = random.choice(browserAgents)
    last = time.time()
    tmpDict = dict()
    for campSiteID, campSite in tmpResponse["campsites"].items():
        tmpDict[campSite["site"]] = campSiteID
    if isAll[i]:
        campSites[i].extend(tmpDict.keys())
    campSiteIDOf.append(tmpDict)
    if i != len(places) - 1:
        time.sleep(random.choice(delay))

while 1:
    for i in range(len(places)):
        tmpDate = datetime.datetime(startDate.year, startDate.month, 1)
        stopDate = datetime.datetime(endDate.year, endDate.month, calendar.monthrange(endDate.year, endDate.month)[1])
        tmpResponses = []
        while tmpDate <= stopDate:
            tmpUrl = campGrounds[places[i]] + "/month?start_date=" + tmpDate.strftime("%Y-%m-%dT%H%%3A%M%%3A%S.000Z")
            url = pre + tmpUrl
            headersDict["referer"] = base + campGrounds[places[i]] + "/availability"
            headersDict["path"] = "/api/camps/availability/campground/" + tmpUrl
            headersDict["start_date"] = tmpDate.strftime("%Y-%m-%dT%H%%3A%M%%3A%S.000Z")
            tmpResponses.append(json.loads(requests.get(url, headers=headersDict).content.decode("utf-8")))
            headersDict["user-agent"] = random.choice(browserAgents)
            tmpDate = tmpDate + datetime.timedelta(calendar.monthrange(tmpDate.year, tmpDate.month)[1])
            if tmpDate <= stopDate:
                time.sleep(random.choice(delay))
        for site in campSites[i]:
            tmpSpots = []
            for tmpResponse in tmpResponses:
                for date, avail in tmpResponse["campsites"][campSiteIDOf[i][site]]["availabilities"].items():
                    tmpDate = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
                    if avail == "Available" and startDate <= tmpDate <= endDate:
                        tmpSpots.append({"campground": places[i], "campSiteID": campSiteIDOf[i][site], "date": datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")})
            j = 0
            while j < len(tmpSpots):
                k = j + 1
                while k < len(tmpSpots) and k - j < maxDays and tmpSpots[k]["date"] == tmpSpots[k - 1]["date"] + datetime.timedelta(days=1):
                    k = k + 1
                if minDays <= k - j <= maxDays:
                    try:
                        reserve(campGrounds[places[i]], campSiteIDOf[i][site], tmpSpots[j]["date"], k - j, tmpSpots[j]["campground"])
                    except Exception as e:
                        print(e)
                j = k
