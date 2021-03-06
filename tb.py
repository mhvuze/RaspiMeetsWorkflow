#!/usr/bin/python

from bs4 import BeautifulSoup as bs
import os
import requests
import sys

# Upload to online service
def uploadCard(cardFile):
    try:
        server = requests.get('https://dropfile.to/getuploadserver').text.strip() + "/upload"
        upload = requests.post(server, files={'file':open(cardFile, 'rb')})
        if(upload.json()['status']==0 and upload.status_code==200):
            print(upload.json()['url'])
        else:
            print("Upload failed in final stage.")
    except:
        print("Upload failed in secondary stage.")

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
            line = line.replace(";CHARSET=ISO-8859-1", "")
            
            if line.startswith("FN:") and line.count(" ") == 1:
                names = line.replace("FN:", "").split(" ")
                f.write(("FN: {0}  {1} \n").format(names[1].strip(), names[0]))
            elif line.startswith("FN:") and line.count(" u. ") == 1:
                names = line.replace("FN:", "").split(" u. ")
                prename = names[0].split(" ")
                f.write(("FN: {0}  {1} u. {2} \n").format(prename[0], prename[1].strip(), names[1].strip()))
            elif line.startswith("N:") and line.count(" ") == 1:
                names = line.replace("N:", "").split(" ")
                f.write(("N:{0};{1};;;\n").format(names[0], names[1].strip()))
            elif line.startswith("N:") and line.count(" u. ") == 1:
                names = line.replace("N:", "").split(" u. ")
                prename = names[0].split(" ")
                f.write(("N:{0};{1} u. {2};;;\n").format(prename[0], prename[1].strip(), names[1].strip()))
            elif line.startswith("VERSION:"):
                f.write("VERSION:3.0\n")
            else:
                f.write(line)

# Basics
header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"}
mode = sys.argv[1]

# Fetch vCard
if mode == "fetch-vcard":
    number = sys.argv[2]
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
            callerName = soup.find_all("div", class_="name")[0].get("title")
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
                    urlCard = "https://adresse.dastelefonbuch.de" + soup.find_all("a", title="Speichern")[0].get("href")
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
