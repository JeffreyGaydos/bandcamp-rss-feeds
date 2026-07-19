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
def updateSsf(links, parserName, user, prefix, newIndicatorString):
    print(f"{prefix} Found {len(links)} links...")

    existingLinks = []
    newLinks = []
    try:
        ssfr = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "r", -1, "utf-8")
        ssfAll = ssfr.read()
        ssfr.close()
        ssfAll = ssfAll.replace(newIndicatorString, "") #remove any "new" indicators for comparison

        existingLinks = ssfAll.splitlines()

        for link in links:
            if(not existingLinks.__contains__(str(link))): # str required when comparing string to int
                newLinks.append(link)
        
        # this is the only trackable object that should handle deletes. The releases for those that were followed will persist when you unfollow
        if(parserName == "following"):
            linksToKeep = []
            for existingLink in existingLinks:
                if(links.__contains__(existingLink)):
                    linksToKeep.append(existingLink)

            removedFollowsCount = len(existingLinks) - len(linksToKeep)
            if(removedFollowsCount > 0):
                print(f"{prefix} Removed {removedFollowsCount} artists that {user} no longer follows")
            ssfw_follow = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "w", -1, "utf-8")
            ssfw_follow.write('\n'.join(linksToKeep))
            ssfw_follow.write('\n') # need a closing newline also
            ssfw_follow.close()

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

# returns any data that was not already found in the internal SSF. This is essentially pre-removing all existing data so we can minimize API calls
def updateInternalSsf(data, fileName, user, prefix):
    print(f"{prefix} Updating Internal File with {len(data)} items...")

    existingData = []
    newData = []
    try:
        ssfr = open(f"{const._ssf_path}/{fileName}_{user}.ssf", "r", -1, "utf-8")
        ssfAll = ssfr.read()
        ssfr.close()

        existingData = ssfAll.splitlines()

        for datum in data:
            if(not existingData.__contains__(str(datum))):
                newData.append(datum)

    except:
        print(f"{prefix} {fileName.capitalize()} SSF for this user DNE, must be a new user.")
        newData = data #if it didn't exist before, it's all new!
    
    print(f"{prefix} Found {len(newData)} new {fileName} items")

    ssfw = open(f"{const._ssf_path}/{fileName}_{user}.ssf", "a", -1, "utf-8")
    
    for newDatum in newData:
        ssfw.write(f"{newDatum}")
        ssfw.write("\n")
    ssfw.close()

    return newData

def prependCurrentDateToSsfIfNecessary(parserName, user):
    ssfr = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "r", -1, "utf-8")
    allContents = ssfr.read()
    possibleDateString = allContents.splitlines()[0]
    ssfr.close()
    try:
        datetime.datetime.fromisoformat(possibleDateString)
    except:
        ssfw = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "w", -1, "utf-8")
        ssfw.write(f"{datetime.datetime.now()}\n{allContents}")
        ssfw.close()


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

def getLinks(source, prefix, querySelectors, urlPostfix):
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
        print(f"{prefix} WARNING Got {len(rawContent)} bytes of data and exhausted all retries.")

    soup = BeautifulSoup(rawContent, 'html.parser')
    # this loop is for the artist "woob" and likely other legacy artists that have a different "music" page than nearly every other artist on bandcamp
    for querySelector in querySelectors:
        linkElements = soup.select(querySelector)
        if(len(linkElements) > 0):
            break

    if(len(linkElements) == 0):
        linkElements = soup.select('meta[property="og:url"]')
        try:
            return [linkElements[0].attrs["content"]] # the artist has exactly 1 tralbum on bandcamp
        except:
            return [] # the artist actually has no tralbums on bandcamp currently
        
    links = []

    for link in linkElements:
        if link.get_attribute_list("href")[0].startswith("/"):
            sanitizedSource = re.sub(f"{urlPostfix}$", "", source) # only remove from the end
            sanitizedSource = sanitizedSource.replace(const._newIndicator, "")
            if sanitizedSource.endswith("/"):
                sanitizedSource = sanitizedSource[:-1]
            link = f"{sanitizedSource}{link.get_attribute_list('href')[0]}"
            links.append(link)
        else:
            links.append(link.get_attribute_list("href")[0])
    return links

# user: the user of a bandcamp page, as dsiplayed in the URL for bandcamp
# parserName: 1 word, suitable for use in logging and file names, lowercase
# urlPostfix: the path to the webpage we are trying to scrape, coming after "https://bandcamp.com/{user}/"
# querySelectors: a list of CSS query selectors that point to a list of links that we want to update on. Will attempt each query in order until at least 1 link is found. Not a union.
# baseUrl: the start base of the URL for which to find links in. For user collections & following, that's "https://bandcamp.com/{user}/"
# forceNotNew: Tells the remaining methods to not treat all incoming links as NEW for this URL, used for newly followed artists' releases
def runGetScrape(user, parserName, urlPostfix, querySelectors, baseUrl, forceNotNew = False):
    process = f"{parserName}_parser"
    prefix = f"[{process}:{user}]:"

    print(f"{prefix} Pinging bandcamp {parserName} feed for user {user} [{baseUrl}/{urlPostfix}]")

    links = []
    links = getLinks(f"{baseUrl}/{urlPostfix}", prefix, querySelectors, urlPostfix)

    if(len(links) == 0):
        # This is usually because the artist does not have any tralbums on bandcamp yet
        print(f"{prefix} WARNING - could not find any links for {baseUrl}/{urlPostfix}")

    if(forceNotNew):
        # When first following an artist, don't display all music as new releases. NOTE: any release that occurs on the same day you follow an artist will not be tracked
        updateSsf(links, parserName, user, prefix, "")
    else:
        updateSsf(links, parserName, user, prefix, const._newIndicator)

def runGet(url, field, subfields, prefix):
    time.sleep(const._pingDelay)
    jsondata = [] #array just so error handling can check length only
    getResponse = {}
    try:
        getResponse = requests.get(url)
    except:
        time.sleep(30)
        try:
            getResponse = requests.get(url)
        except:
            print(f"{prefix} Could not GET {url}")
    try:
        jsondata = getResponse.json()[field]
    except:
        wee = 1
        #print(f"{prefix} (possibly expected) Could not find {field} field in GET {url}")
    if(len(subfields) > 0):
        items = []
        try:
            for data in jsondata:
                drilldown = data
                for subfield in subfields:
                    drilldown = drilldown[subfield]
                else:
                    items.append(drilldown)
        except:
            print(f"{prefix} Could not find one or more subfields for {field}")
        return items
    else:
        return jsondata

# user: the username of the bandcamp user we are pinging for
# fanID: The internal ID bandcamp uses for a specific user, should be placed in users.ssf after each username with a space in between
# parserName: 1 word, suitable for use in logging and file names, lowercase
# urlPostfix: The endpoint you want to ping. Known endpoints include: "collection_items", "wishlist_items", "following_bands"
# tokenPostfix: Some of the bandcamp endpoints require a special postfix on the end of the older_than_token
# field: the top level field that we will loop through
# subfields: an array of subfields on the objects we are looping through that leads to the field we want
# raw: set to true if you want the raw data from whatever subfield you are accessing (i.e. no URL wrap)
def runGetReleases(user, fanID, parserName, artist_id, field, subfields, newArtist=False):
    process = f"{parserName}_parser"
    prefix = f"[{process}:{user}]:"
    items = runGet(f"{const._bandcampReleasesEndpoint}?band_id={artist_id}", field, subfields, prefix)
    finalItems = [f"{artist_id}:{x}" for x in items]
    # newItems = updateInternalSsf(items, "discography_item_ids", user, prefix)
    # newLinks = []
    # for newItem in newItems:
    #     albumLink = runGet(f"{const._bandcampTralbumDetailsEndpoint}?band_id={artist_id}&tralbum_id={newItem}&tralbum_type=a", "bandcamp_url", [], prefix)
    #     if(len(albumLink) == 0):
    #         trackLink = runGet(f"{const._bandcampTralbumDetailsEndpoint}?band_id={artist_id}&tralbum_id={newItem}&tralbum_type=t", "bandcamp_url", [], prefix)
    #         newLinks.append(trackLink)
    #     else:
    #         newLinks.append(albumLink)
    updateSsf(finalItems, parserName, user, prefix, "" if newArtist else const._newIndicator)

# user: the username of the bandcamp user we are pinging for
# fanID: The internal ID bandcamp uses for a specific user, should be placed in users.ssf after each username with a space in between
# parserName: 1 word, suitable for use in logging and file names, lowercase
# urlPostfix: The endpoint you want to ping. Known endpoints include: "collection_items", "wishlist_items", "following_bands"
# tokenPostfix: Some of the bandcamp endpoints require a special postfix on the end of the older_than_token
# field: the top level field that we will loop through
# subfields: an array of subfields on the objects we are looping through that leads to the field we want
# raw: set to true if you want the raw data from whatever subfield you are accessing (i.e. no URL wrap)
def runPost(user, fanID, parserName, urlPostfix, tokenPostfix, field, subfields):
    process = f"{parserName}_parser"
    prefix = f"[{process}:{user}]:"
    time.sleep(const._pingDelay)
    jsondata = []
    try:
        postResponse = requests.post(f"{const._bandcampCollectionAPI}/{urlPostfix}", f"{{\"fan_id\":{fanID},\"older_than_token\":\"9999999999:9999999999{tokenPostfix}\",\"count\":1000000}}")
        jsondata = postResponse.json()[field]
    except:
        time.sleep(30)
        try:
            postResponse = requests.post(f"{const._bandcampCollectionAPI}/{urlPostfix}", f"{{\"fan_id\":{fanID},\"older_than_token\":\"9999999999:9999999999{tokenPostfix}\",\"count\":1000000}}")
            jsondata = postResponse.json()[field]
        except:
            print(f"{prefix} Could not post for {field}")
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
    
    if(parserName == "following"):
        artists = []
        for data in jsondata:
            artists.append(data['band_id'])
        newArtists = updateInternalSsf(artists, "band_ids", user, prefix)
        # we need to know both the existing artists and the new artists to avoid notifying all tracks when you follow
        return [[existingArtists for existingArtists in artists if existingArtists not in newArtists], newArtists]

def unNewSsf(parserName, user):
    ssfr = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "r", -1, "utf-8")
    ssfAll = ssfr.read()
    ssfr.close()
    ssfAll = ssfAll.replace(const._newIndicator, "") #remove any "new" links from before
    # actually write to remove the new indicators
    ssfw = open(f"{const._ssf_path}/{parserName}_{user}.ssf", "w", -1, "utf-8")
    ssfw.write(ssfAll)
    ssfw.close()

def getFanIdFromUsername(username):
    requestsResponse = requests.get(f"https://bandcamp.com/{username}", headers={'user-agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    rawContent = requestsResponse.content

    soup = BeautifulSoup(rawContent, 'html.parser')
    
    if(len(soup.select('div#pagedata')) > 0 and soup.select('div#pagedata')[0].has_attr("data-blob")):
        allData = soup.select('div#pagedata')[0]["data-blob"]
        fanId = json.loads(allData)["fan_data"]["fan_id"]
        return fanId
    else:
        print("Unable to find user page. Make sure your bandcamp profile is set to be \"public\"!")
        return None
