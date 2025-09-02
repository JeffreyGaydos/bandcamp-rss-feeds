import time
import datetime
import requests
import const
from bs4 import BeautifulSoup
import re
import json

# links: the array of links output from the calling function; a list of links we want to update on
# parserName: the parserName from the calling function
# user: the user from the calling function
# prefix: the logging prefix from the calling function
# TODO: Test that a new user will populate properly
# TODO: Test that losing internet connection will retry and work properly
# TODO: Test idempotency
# TODO: Test "newSource = True" whatever that is supposed to do
# TODO: Automated tests??
# TODO: Refactor artists tracking what the heck dude
def updateSsf(links, parserName, user, prefix, newIndicatorString):
    print(f"{prefix} Found {len(links)} links...")

    existingLinks = []
    newLinks = []
    try:
        ssfr = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "r", -1, "utf-8")
        ssfAll = ssfr.read()
        ssfr.close()
        ssfAll = ssfAll.replace(newIndicatorString, "") #remove any "new" links from before
        existingLinks = ssfAll.splitlines()

        for link in links:
            if(not existingLinks.__contains__(link)):
                newLinks.append(link)
    except:
        print(f"{prefix} {parserName.capitalize()} SSF for this user DNE, must be a new user.")
        newLinks.append(links)

    print(f"{prefix} Found {len(newLinks)} new {parserName} items")

    ssfw = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "a", -1, "utf-8")
    
    for newLink in newLinks:
        ssfw.write(f"{newIndicatorString}{newLink}")
        ssfw.write("\n")
    ssfw.close()

    print(f"{prefix} Exited successfully")

def isItBandcampFriday():
    time.sleep(const._pingDelay)
    requestsResponse = requests.get(f"https://isitbandcampfriday.com/", headers={'user-agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    rawContent = requestsResponse.content

    soup = BeautifulSoup(rawContent, 'html.parser')
    #yesWord = soup.select('span.next-fundraiser')
    if(len(soup.select('div#bandcamp-friday-vm')) > 0 and soup.select('div#bandcamp-friday-vm')[0].has_attr("data-fundraisers")):
        nextDates = soup.select('div#bandcamp-friday-vm')[0]["data-fundraisers"]

        theNextDate = json.loads(nextDates)[0]["display"]

        theNextDate = theNextDate.replace("th,", "")
        theNextDate = theNextDate.replace("st,", "")
        theNextDate = theNextDate.replace("rd,", "")
        theNextDate = theNextDate.replace("nd,", "")
        dateOfNextBandcampFriday = datetime.datetime.strptime(theNextDate, '%B %d %Y')
        today = datetime.datetime.now().date()
        isItThough = dateOfNextBandcampFriday == datetime.datetime(today.year, today.month, today.day)

        return isItThough
    else:
        print("Unable to find next bandcamp Friday. Recieved: " + soup.text)
        print("Here's the raw HTML: " + (str)(rawContent))
        return False

def getLinks(source, prefix, querySelector, urlPostfix):
    time.sleep(const._pingDelay)
    requestsResponse = requests.get(f"{source.replace(const._newIndicator, '')}", headers={'user-agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    rawContent = requestsResponse.content

    retry = 1
    while(len(rawContent) == 0 and retry < 33):
        if(len(rawContent) == 0):
            print(f"{prefix} Got {len(rawContent)} bytes of data. Retrying...")
            time.sleep(retry)
            retry *= 2
            requestsResponse = requests.get(f"{source.replace(const._newIndicator, '')}", headers={'user-agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
            rawContent = requestsResponse.content
        else:
            print(f"{prefix} Got {len(rawContent)} bytes of data.")
    
    if(len(rawContent) == 0):
        print(f"{prefix} [WARNING] Got {len(rawContent)} bytes of data and exhausted all retries.")

    soup = BeautifulSoup(rawContent, 'html.parser')
    linkElements = soup.select(querySelector)
    links = []

    for link in linkElements:
        if link.get_attribute_list("href")[0].startswith("/"):
            sanitizedSource = re.sub(f"{urlPostfix}$", "", source) # only remove from the end
            if sanitizedSource.endswith("/"):
                sanitizedSource = sanitizedSource[:-1]
            link = f"{sanitizedSource}{link.get_attribute_list('href')[0]}"
            links.append(link)
        else:
            links.append(link.get_attribute_list("href")[0])
    return links

# user: the user of a bandcamp page, as dsiplayed in the URL for bandcamp
# parserName: 1 word, suitable for use in logging and file names, lowercase
# urlPostfix: the path to the webpage we are trying to scrape, coming after "https://bandcamp.com/{_user}/"
# querySelector: a CSS query selector that points to a list of links that we want to update on
def runGet(user, parserName, urlPostfix, querySelector, forceNotNew = False, baseUrl = "https://bandcamp.com"):
    process = f"{parserName}_parser.py"
    prefix = f"[{process}:{user}]:"

    print(f"{prefix} Pinging bandcamp {parserName} feed for user {user}")

    links = getLinks(f"{baseUrl}/{user}/{urlPostfix}", prefix, querySelector, urlPostfix)

    if(forceNotNew):
        # When first following an artist, don't display all music as new releases. NOTE: any release that occurs on the same day you follow an artist will not be tracked
        updateSsf(links, parserName, user, prefix, "")
    else:
        updateSsf(links, parserName, user, prefix, const._newIndicator)

# user: the username of the bandcamp user we are pinging for
# fanID: The internal ID bandcamp uses for a specific user, should be placed in users.ssf after each username with a space in between
# parserName: 1 word, suitable for use in logging and file names, lowercase
# urlPostfix: The endpoint you want to ping. Known endpoints include: "collection_items", "wishlist_items", "following_bands"
# tokenPostfix: Some of the bandcamp endpoints require a special postfix on the end of the older_than_token
# field: the top level field that we will loop through
# subfields: an array of subfields on the objects we are looping through that leads to the field we want
# raw: set to true if you want the raw data from whatever subfield you are accessing (i.e. no URL wrap)
def runPost(user, fanID, parserName, urlPostfix, tokenPostfix, field, subfields):
    process = f"{parserName}_parser.py"
    prefix = f"[{process}:{user}]:"
    time.sleep(const._pingDelay)
    postResponse = requests.post(f"{const._bandcampCollectionAPI}/{urlPostfix}", f"{{\"fan_id\":{fanID},\"older_than_token\":\"9999999999:9999999999{tokenPostfix}\",\"count\":1000000}}")
    jsondata = postResponse.json()[field]
    links = []
    for data in jsondata:
        drilldown = data
        for subfield in subfields:
            drilldown = drilldown[subfield]
        if parserName == "following":
            links.append(f"https://{drilldown}.bandcamp.com{const._musicPostfix}")
        else:
            links.append(drilldown)
    
    updateSsf(links, parserName, user, prefix, const._newIndicator)