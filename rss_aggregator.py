import sys
import datetime
import re
import const

_process = "rss_aggregator.py"
_user = "unknown user..."
_prefix = f"[{_process}:{_user}]:"

def createItem(titlePrefix, guidPrefix, date, links, user):
    item = open("./item.rss").read()

    item = item.replace(const._title, f"{titlePrefix}**{user}**")
    item = item.replace(const._guid, f"{guidPrefix}-{(str)(date).replace(' ', '_')}-{user}")
    item = item.replace(const._links, links.replace("\n", " "))
    item = item.replace(const._date, f"{date}")

    print(f"{_prefix} Created item {titlePrefix}**{user}**")
    return item

def run(user):
    _user = user
    _prefix = f"[{_process}:{_user}]:"

    cutoffDate = datetime.datetime.now()
    cutoffDate = cutoffDate.__add__(datetime.timedelta(seconds=-21600))
    items = []

    wishlistFile = open(f"{const._ssf_path}/wishlist_{_user}.ssf")
    wishlistDate = datetime.datetime.fromisoformat((wishlistFile.readline())[0:-1])
    wishlistLinks = wishlistFile.read().splitlines()
    newWishlistLinks = []
    for link in wishlistLinks:
        if link.startswith(const._newIndicator):
            newWishlistLinks.append(link.replace(const._newIndicator, ""))
    wishlistHasUpdate = wishlistDate > cutoffDate and len(newWishlistLinks) > 0

    if wishlistHasUpdate:
        items.append(createItem("Wishlist Update for ", "wishlist", wishlistDate, " ".join(newWishlistLinks), _user))

    #update RSS file
    if len(items) > 0:
        print(f"{_prefix} updating items.rss with {len(items)} updates for this user")

        itemsrss = open("./items.rss", "a", -1, "utf-8")
        itemsrss.write("\n".join(items))
        itemsrss.write("\n")
        itemsrss.close()
        return True
    else:
        print(f"{_prefix} No updates detected for this user")    
        print(f"{_prefix} Exited successfully")
        return False