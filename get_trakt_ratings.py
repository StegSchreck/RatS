#!/usr/bin/env python
import csv
import os

from parsers.trakt_parser import TraktRatingsParser

if __name__ == "__main__":
    trakt_parser = TraktRatingsParser()
    result = trakt_parser.parse()
    with open(os.path.dirname(__file__) + 'trakt.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(result)
