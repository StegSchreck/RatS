#!/usr/bin/env python
import datetime
import os
import time

from RatS.data import file_handler
from RatS.parsers.trakt_parser import TraktRatingsParser

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'exports'))
JSON_FILE = os.path.join(EXPORTS_FOLDER, TIMESTAMP + '_trakt.json')
CSV_FILE = os.path.join(EXPORTS_FOLDER, TIMESTAMP + '_trakt.csv')

if __name__ == "__main__":
    trakt_parser = TraktRatingsParser()
    movies = trakt_parser.parse()
    file_handler.save_movies_json(movies, JSON_FILE)
    print('===== saved parsed movies to %s =====' % JSON_FILE)
    # loaded_movies = file_handler.load_movies_json(JSON_FILE)
