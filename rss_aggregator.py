import datetime
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

# user
# parsers: a list of parserNames that were input into the generic_parser
def run(user, parsers):
    _user = user
    _prefix = f"[{_process}:{_user}]:"

    cutoffDate = datetime.datetime.now()
    cutoffDate = cutoffDate.__add__(datetime.timedelta(seconds=-21600))
    items = []

    for parser in parsers:
        ssf = open(f"{const._ssf_path}/{parser}_{_user}.ssf")
        ssfDate = datetime.datetime.fromisoformat((ssf.readline())[0:-1])
        ssfLinks = ssf.read().splitlines()
        newSsfLinks = []
        for link in ssfLinks:
            if link.startswith(const._newIndicator):
                newSsfLinks.append(link.replace(const._newIndicator, ""))
        if ssfDate > cutoffDate and len(newSsfLinks) > 0:
            items.append(createItem(f"{parser.capitalize()} update for ", parser, ssfDate, " ".join(newSsfLinks), _user))

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