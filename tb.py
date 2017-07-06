#!/usr/bin/python

from bs4 import BeautifulSoup as bs
import requests
import sys

# Basics
header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"}

number = sys.argv[1]
urlSearch = "https://www.dastelefonbuch.de/Rückwärts-Suche/" + number

# Get result page
try:
    site = requests.get(urlSearch, headers=header)
    soup = bs(site.content, 'html.parser')
except:
    print("Error during urlSearch fetch.")
else:
    # Get result entries for number
    try:
        urlResult = soup.find_all("a", class_=" name")[0].get("href")
    except:
        print("No entries found.")
    else:
        # Get entry page
        try:
            site = requests.get(urlResult, headers=header)
            soup = bs(site.content, 'html.parser')
        except:
            print("Error during urlResult fetch.")
        else:
            # Get url for vCard from entry page
            try:
                urlCard = "https://adresse.dastelefonbuch.de" + soup.find_all("a", title="Speichern")[0].get("href")
                print(urlCard)
            except:
                print("Error during vCard fetch.")

# Debug
#print(urlSearch)
#print(urlResult)
#print(urlCard)
