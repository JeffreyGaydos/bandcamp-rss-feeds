import sys
import datetime
import requests
import re
import const
from bs4 import BeautifulSoup

_process = "wishlist_parser.py"

def run(user):
    _user = user
    _prefix = f"[{_process}:{_user}]:"

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

    prefixedLinks = []
    countNewLinks = 0
    try:
        ssfr = open(f"{const._ssf_path}/wishlist_{_user}.ssf", "r", -1, "utf-8")
        ssfAll = ssfr.read()
        ssfr.close()
        for link in links:
            if not ssfAll.__contains__(link):
                prefixedLinks.append(f"{const._newIndicator}{link}")
                countNewLinks += 1
            if ssfAll.__contains__(link):
                prefixedLinks.append(f"{link}")
    except:
        print(f"{_prefix} Wishlist SSF for this user DNE, must be a new user.")
        for link in links:
            prefixedLinks.append(f"NEW: {link}")
    print(f"{_prefix} Found {countNewLinks} new wishlist items")

    ssfw = open(f"{const._ssf_path}/wishlist_{_user}.ssf", "w", -1, "utf-8")
    
    ssfw.write((str)(datetime.datetime.now()))
    ssfw.write("\n")
    for link in prefixedLinks:
        ssfw.write(link)
        ssfw.write("\n")
    ssfw.close()

    print(f"{_prefix} Exited successfully")