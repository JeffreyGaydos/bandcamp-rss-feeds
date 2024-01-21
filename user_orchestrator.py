import sys
import const
import datetime
import re
import rss_aggregator
import wishlist_parser

_process = re.compile(r"[^\\\/]+$").search(sys.argv[0]).group(0)
_prefix = f"[{_process}]:"

print(f"{_prefix} Starting")
print(f"{_prefix} Clearing existing items from items.rss")
items = open("items.rss", "w", -1, "utf-8")
items.write("")
items.close()

update = False

for user in open("users.ssf").read().split("\n"):
    wishlist_parser.run(user)
    thisUpdate = rss_aggregator.run(user)
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