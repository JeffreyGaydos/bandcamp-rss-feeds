import sys
import const
import datetime
import re

_process = re.compile(r"[^\\\/]+$").search(sys.argv[0]).group(0)
_prefix = f"[{_process}]:" # The GHA will repeat this for all users looping through the users.ssf

sys.argv[1] = "bsg" #TODO: Read users file to get cli args and loop here
exec(open("rss_aggregator.py").read())

#transfer items to final
dateString = (str)(datetime.datetime.now())
print(f"{_prefix} Updating final.rss at {dateString}")

base = open("./base.rss").read()
base = base.replace(const._date, dateString)
base = base.replace(const._items, open("./items.rss").read())

rss = open("./final.rss", "w", -1, "utf-8")
rss.write(base)
rss.close()

print(f"{_prefix} Exited successfully")