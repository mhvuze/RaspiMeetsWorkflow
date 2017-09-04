#!/usr/bin/python

from bs4 import BeautifulSoup as bs
import os
import requests
import sys

# Move to local server
def moveCard(cardFile):
    try:
        os.rename(cardFile, "/var/www/html/temp.vcf")
        print("http://192.168.2.121/temp.vcf")
    except:
        print("Moving file to server failed.")

# Clean up vCard, reformat name if that's simple
def cleanCard(cardFile, cardContent):
    with open(cardFile, 'w', encoding='utf-8') as f:
        for line in cardContent:
            line = line.replace(";CHARSET=Windows-1252", "")
            
            if line.startswith("NOTE:gefunden auf"):
                pass
            else:
                f.write(line)

# Basics
header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"}
mode = sys.argv[1]

# Fetch vCard
if mode == "fetch-vcard":
    number = sys.argv[2]
    urlSearch = "https://www.telefonabc.at/result.aspx?what=" + number

    # Get result page
    try:
        site = requests.get(urlSearch, headers=header)
        soup = bs(site.content, 'html.parser')
    except:
        print("Error during urlSearch fetch.")
    else:
        # Get result entries for number
        try:
            urlResult = soup.find_all("a", {"itemprop":"url"})[0].get("href")
            callerName = soup.find_all("h3", {"itemprop":"name"})[0].text.strip()
            print(callerName)
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
                # Get url for vCard from entry page and save it offline
                try:
                    urlCard = soup.find_all("a", {"data-original-title":"VISITENKARTE"})[0].get("href")
                    site = requests.get(urlCard, headers=header)
                    cardContent = bs(site.content, 'html.parser').text

                    with open('./temp.vcf', 'w', encoding='utf-8') as f:
                        f.write(cardContent)

                    print(urlCard + ";;;" + callerName)
                except:
                    print("Error during vCard fetch.")
# Modify vCard
elif mode == "mod-vcard":
    organisation = sys.argv[2]

    # Handle missing organisation
    if organisation == "":
        with open('./temp.vcf', 'r', encoding='utf-8') as f:
            cardContent = f.readlines()
        
        cleanCard('./temp.vcf', cardContent)
        #uploadCard('./temp.vcf')
        moveCard('./temp.vcf')
    
    # Open base vCard
    else:
        try:
            with open('./temp.vcf', 'r', encoding='utf-8') as f:
                cardContent = f.readlines()
            try:
                # Add organisation to vCard
                cardContent = cardContent[:-1]
                cardContent.append("ORG:%s;\n" % organisation)
                cardContent.append("END:VCARD")

                cleanCard('./temp.vcf', cardContent)
                
                # Process new vCard
                try:
                    #uploadCard('./temp.vcf')
                    moveCard('./temp.vcf')
                    os.remove('./temp.vcf')
                except:
                    print("Error during final vCard handling.")
            except:
                print("Error during vCard modification.")
        except:
            print("Could not open base vCard.")