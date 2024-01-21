import sys
import datetime
import re
import const

_process = re.compile(r"[^\\\/]+$").search(sys.argv[0]).group(0)
_user = sys.argv[1]
_prefix = f"[{_process}:{_user}]:" # The GHA will repeat this for all users looping through the users.ssf

def createItem(titlePrefix, guidPrefix, date, links):
    item = open("./item.rss").read()

    item = item.replace(const._title, f"{titlePrefix}**{_user}**")
    item = item.replace(const._guid, f"{guidPrefix}-{(str)(date).replace(' ', '_')}-{_user}")
    item = item.replace(const._links, links.replace("\n", " "))
    item = item.replace(const._date, f"{date}")

    print(f"{_prefix} Created item {titlePrefix}**{_user}**")
    return item

cutoffDate = datetime.datetime.now()
cutoffDate = cutoffDate.__add__(datetime.timedelta(seconds=-21600))
items = []

wishlistFile = open(f"{const._ssf_path}/wishlist_{_user}.ssf")
wishlistDate = datetime.datetime.fromisoformat((wishlistFile.readline())[0:-1])
wishlistLinks = wishlistFile.read()
wishlistHasUpdate = wishlistDate > cutoffDate

if wishlistHasUpdate:
    items.append(createItem("Wishlist Update for ", "wishlist", wishlistDate, wishlistLinks))

#update RSS file
if len(items) > 0:
    print(f"{_prefix} updating items.rss with {len(items)} updates for this user")

    itemsrss = open("./items.rss", "a", -1, "utf-8")
    itemsrss.write("\n".join(items))
    itemsrss.write("\n")
    itemsrss.close()
else:
    print(f"{_prefix} No updates detected for this user")    

print(f"{_prefix} Exited successfully")