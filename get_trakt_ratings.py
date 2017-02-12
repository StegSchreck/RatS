#!/usr/bin/env python
import csv
import json
import os

from parsers.trakt_parser import TraktRatingsParser

if __name__ == "__main__":
    trakt_parser = TraktRatingsParser()
    movies = trakt_parser.parse()
    with open(os.path.dirname(__file__) + '/exports/trakt.json', 'w') as jsonfile:
        movies_json = [m.to_json() for m in movies]
        jsonfile.write(json.dumps(movies_json))
        jsonfile.close()
    #with open(os.path.dirname(__file__) + '/exports/trakt.csv', 'w') as csvfile:
    #    writer = csv.writer(csvfile)
    #    writer.writerows(movies)
    #    csvfile.close()

