import sys
import const
import datetime
import re
import rss_aggregator
import generic_parser
import os

_process = re.compile(r"[^\\\/]+$").search(sys.argv[0]).group(0)
_prefix = f"[{_process}]:"

print(f"{_prefix} Starting")
print(f"{_prefix} Clearing existing items from items.rss")
items = open("items.rss", "w", -1, "utf-8")
items.write("")
items.close()

supportedSSFTypes = ["collection", "following", "release", "wishlist"]

def getUsers():
    users = []
    usersReadFile = open("users.ssf", "r")
    needsRewrite = False
    for userTuple in usersReadFile.read().split("\n"):
        if(len(userTuple) == 0):
            #empty line, ignore
            continue
        if(len(userTuple.split(" ")) == 1):
            username = userTuple.split(" ")[0]
            print(f"{_prefix} user.sff missing fan_id for user {username}. Finding automatically...")
            fanId = generic_parser.getFanIdFromUsername(userTuple.split(" ")[0])
            users.append([username, fanId])
            needsRewrite = True
        else:
            users.append([userTuple.split(" ")[0], userTuple.split(" ")[1]])
    usersReadFile.close()

    if(needsRewrite):
        print(f"{_prefix} writing fan_ids to user.ssf for all users")
        usersWriteFile = open("users.ssf", "w")
        for userTuple in users:
            usersWriteFile.write(f"{userTuple[0]} {userTuple[1]}\n")
        usersWriteFile.close()
    return users

def prepSSFs(usersArray):
    print(f"{_prefix} Prepping SSF files based on current users...")
    fileList = os.listdir('SSF')
    # delete any existing files that are not for a user found in the users.ssf file
    for fileName in fileList:
        matchesUser = False
        for userTuple in usersArray:
            username = userTuple[0]
            if(fileName.endswith(f"{username}.ssf")):
                matchesUser = True
                break
        if(not matchesUser):
           os.remove(f"SSF/{fileName}")

    # add any files (empty) that are not present
    for userTuple in usersArray:
        username = userTuple[0]
        for type in supportedSSFTypes:
            try:
                fileList.index(f"{type}_{username}.ssf")
            except:
                newStubFile = open(f"SSF/{type}_{username}.ssf", "w")
                newStubFile.write(f"{datetime.datetime.now()}\n")
                newStubFile.close()

update = False
users = getUsers()
prepSSFs(users)

for userTuple in users:    
    user = userTuple[0]
    fanId = userTuple[1]
    for type in supportedSSFTypes:
        generic_parser.unNewSsf(type, user)
    generic_parser.runPost(user, fanId, "following", "following_bands", "", "followeers", ["url_hints", "subdomain"])
    generic_parser.runPost(user, fanId, "collection", "collection_items", ":p::", "items", ["item_url"])
    generic_parser.runPost(user, fanId, "wishlist", "wishlist_items", ":a::", "items", ["item_url"])
    followFile = open(f"{const._ssf_path}/following_{user}.ssf")
    followFile.readline()
    artists = followFile.read().splitlines()
    followFile.close()
    for artist in artists:
        # When you follow an artist, their current releases should NOT show up as new
        # this alternative query selector is for the artist "woob" and likely other legacy artists that have a different "music" page than nearly every other artist on bandcamp
        generic_parser.runGet(user, "release", "music", ["ol.music-grid li.music-grid-item a", ".ipCellLabel1 a"], artist[:-len(const._musicPostfix)], artist.startswith(const._newIndicator))
    for type in supportedSSFTypes:
        generic_parser.prependCurrentDateToSsfIfNecessary(type, user)

    thisUpdate = rss_aggregator.run(user, ["collection", "following", "wishlist", "release"])
    update = thisUpdate or update

_process = re.compile(r"[^\\\/]+$").search(sys.argv[0]).group(0)
_prefix = f"[{_process}]:"

# add notification on Thursday (4) so that it will appear Friday morning
#if(datetime.datetime.today().weekday() == 4 and datetime.datetime.today().day <= 7):
if(generic_parser.isItBandcampFriday()):
    rss_aggregator.addBandcampFridayItem()
    update = True

#transfer items to final
if update:
    dateString = (str)(datetime.datetime.now())
    print(f"{_prefix} Updating final.rss at {dateString}")

    base = open("./base.rss").read()
    base = base.replace(const._date, dateString)
    base = base.replace(const._items, open("./items.rss").read())

    rss = open("./final.rss", "w", -1, "utf-8")
    rss.write(base)
    rss.close()
else:
    print(f"{_prefix} No updates found for final.rss")

print(f"{_prefix} Exited successfully")