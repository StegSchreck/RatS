#!/usr/bin/env python
import datetime
import os
import sys
import time

from RatS.data import file_handler
from RatS.parsers.trakt_parser import TraktRatingsParser

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))
JSON_FILE = TIMESTAMP + '_trakt.json'
CSV_FILE = TIMESTAMP + '_trakt.csv'

if __name__ == "__main__":
    trakt_parser = TraktRatingsParser()
    movies = trakt_parser.parse()
    file_handler.save_movies_json(movies, EXPORTS_FOLDER, JSON_FILE)
    sys.stdout.write('\r\n===== saved parsed movies to %s/%s =====' % (EXPORTS_FOLDER, JSON_FILE))
    sys.stdout.flush()
    # loaded_movies = file_handler.load_movies_json(JSON_FILE)
