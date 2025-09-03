#https://docs.python.org/3/library/unittest.html
import unittest
import time
import datetime
import requests
import const
from bs4 import BeautifulSoup
import re
import json
import generic_parser

class GenericParserTests(unittest.TestCase):
    previousSsfs = []
    parserTypes = ["collection", "following", "release", "wishlist"]
    users = []

    def setUp(self):
        user_ssfr = open(f"./users.ssf", "r", -1, "utf-8")
        self.users = user_ssfr.read().splitlines()
        user_ssfr.close()
        for parserName in self.parserTypes:
            for user in self.users:
                username = user.split(" ")[0]
                ssfr = open(f"{const._ssf_path}/{parserName}_{username}.ssf", "r", -1, "utf-8")
                self.previousSsfs.append(ssfr.read())

    def tearDown(self):
        i = 0
        for parserName in self.parserTypes:
            for user in self.users:
                username = user.split(" ")[0]
                ssfw = open(f"{const._ssf_path}/{parserName}_{username}.ssf", "w", -1, "utf-8")
                ssfw.write(self.previousSsfs[i])
                i += 1
                
    def AssertExpectedNewIndicators(self, numNewIndicators, contents):
        self.assertEquals(len(contents.split(const._newIndicator)), numNewIndicators + 1, f"Expected {numNewIndicators} 'NEW: ' strings.")

    def test_generic_parser_new_user_1_collection_update(self):
        ssfw = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "w", -1, "utf-8")
        ssfw.write("")
        ssfw.close()
        generic_parser.updateSsf(["https://link1.com"], "collection", "jeffg__g", "", const._newIndicator)
        ssfr = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "r", -1, "utf-8")
        contents = ssfr.read()
        self.assertIn(const._newIndicator, contents)

    def test_generic_parser_new_user_2_collection_updates(self):
        ssfw = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "w", -1, "utf-8")
        ssfw.write("")
        ssfw.close()
        generic_parser.updateSsf(["https://link1.com", "https://link2.com"], "collection", "jeffg__g", "", const._newIndicator)
        ssfr = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "r", -1, "utf-8")
        contents = ssfr.read()
        self.AssertExpectedNewIndicators(2, contents)

    def test_generic_parser_existing_link(self):
        ssfw = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "w", -1, "utf-8")
        ssfw.write("2025-04-04 00:00:00.000\nhttps://link1.com\n")
        ssfw.close()
        generic_parser.updateSsf(["https://link1.com"], "collection", "jeffg__g", "", const._newIndicator)
        ssfr = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "r", -1, "utf-8")
        contents = ssfr.read()
        self.AssertExpectedNewIndicators(0, contents)

    def test_generic_parser_2_existing_links(self):
        ssfw = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "w", -1, "utf-8")
        ssfw.write("2025-04-04 00:00:00.000\nhttps://link1.com\nhttps://link2.com\n")
        ssfw.close()
        generic_parser.updateSsf(["https://link1.com", "https://link2.com"], "collection", "jeffg__g", "", const._newIndicator)
        ssfr = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "r", -1, "utf-8")
        contents = ssfr.read()
        self.AssertExpectedNewIndicators(0, contents)

    def test_generic_parser_existing_and_new_link(self):
        ssfw = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "w", -1, "utf-8")
        ssfw.write("2025-04-04 00:00:00.000\nhttps://link1.com\n")
        ssfw.close()
        generic_parser.updateSsf(["https://link1.com", "https://link2.com"], "collection", "jeffg__g", "", const._newIndicator)
        ssfr = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "r", -1, "utf-8")
        contents = ssfr.read()
        self.AssertExpectedNewIndicators(1, contents)

    def test_generic_parser_0_links_returned_maintains(self):
        ssfw = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "w", -1, "utf-8")
        ssfw.write("2025-04-04 00:00:00.000\nhttps://link1.com\nhttps://link2.com\n")
        ssfw.close()
        generic_parser.updateSsf([], "collection", "jeffg__g", "", const._newIndicator)
        ssfr = open(f"{const._ssf_path}/collection_jeffg__g.ssf", "r", -1, "utf-8")
        contents = ssfr.read()
        self.AssertExpectedNewIndicators(0, contents)
        self.assertEquals(len(contents.split("\n")), 4, "Expected 4 lines.")

if __name__ == '__main__': #starts the tests
    unittest.main()