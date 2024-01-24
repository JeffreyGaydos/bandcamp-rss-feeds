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

update = False

for userTuple in open("users.ssf").read().split("\n"):
    user = userTuple.split(" ")[0]
    fanId = userTuple.split(" ")[1]
    # generic_parser.run(user, "wishlist", "wishlist", "ol.collection-grid  .collection-title-details .item-link")
    # generic_parser.run(user, "following", "following/artists_and_labels", "div.fan-info a.fan-username")
    # generic_parser.run(user, "collection", "", "div.collection-items div.collection-title-details a.item-link")
    generic_parser.runPost(user, fanId, "following", "following_bands", "", "followeers", ["url_hints", "subdomain"])
    generic_parser.runPost(user, fanId, "collection", "collection_items", ":p::", "items", ["item_url"])
    generic_parser.runPost(user, fanId, "wishlist", "wishlist_items", ":a::", "items", ["item_url"])
    followFile = open(f"{const._ssf_path}/following_{user}.ssf")
    followFile.readline()
    artists = followFile.read().splitlines()
    followFile.close()
    generic_parser.runGet(user, "release", "music", "ol.music-grid li.music-grid-item a", artists)
    thisUpdate = rss_aggregator.run(user, ["wishlist", "following", "collection", "release"])
    update = thisUpdate or update

_process = re.compile(r"[^\\\/]+$").search(sys.argv[0]).group(0)
_prefix = f"[{_process}]:"

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