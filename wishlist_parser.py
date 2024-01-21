import sys
import datetime
import requests
import re
import const
from bs4 import BeautifulSoup

_process = "wishlist_parser.py"
_user = sys.argv[1]
_prefix = f"[{_process}:{_user}]:"

def run():
    print(f"{_prefix} Pinging bandcamp wishlist feed for user {_user}")

    requestsResponse = requests.get(f"https://bandcamp.com/{_user}/wishlist", headers={'user-agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'})
    rawContent = requestsResponse.content

    print(f"{_prefix} Got {len(rawContent)} bytes of data.")

    soup = BeautifulSoup(rawContent, 'html.parser')
    linkElements = soup.select("ol.collection-grid  .collection-title-details .item-link")
    links = []
    for link in linkElements:
        links.append(link.get_attribute_list("href")[0])

    print(f"{_prefix} Found {len(links)} links...")

    newLinks = []
    ssfr = open(f"{const._ssf_path}/wishlist_{_user}.ssf", "r", -1, "utf-8")
    ssfAll = ssfr.read()
    ssfr.close()
    for link in links:
        if not ssfAll.__contains__(link):
            newLinks.append(link)
        if ssfAll.__contains__(link):
            break
    print(f"{_prefix} Found {len(newLinks)} new wishlist items")

    if len(newLinks) > 0:
        ssfw = open(f"{const._ssf_path}/wishlist_{_user}.ssf", "w", -1, "utf-8")
        ssfw.write((str)(datetime.datetime.now()))
        ssfw.write("\n")
        for link in newLinks:
            ssfw.write(link)
            ssfw.write("\n")
        ssfw.close()

    print(f"{_prefix} Exited successfully")