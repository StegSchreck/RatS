#!/usr/bin/env python
import datetime
import os
import sys
import time

from RatS.data import file_handler
from RatS.inserters.movielense_inserter import MovielenseInserter
from RatS.parsers.trakt_parser import TraktRatingsParser

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))
JSON_FILE = TIMESTAMP + '_trakt.json'
CSV_FILE = TIMESTAMP + '_trakt.csv'


def main():
    # PARSING DATA
    movies = parse_data_from_source(TraktRatingsParser())
    # FILE LOADING
    # movies = load_data_from_file('20170224211816_trakt.json')
    # POSTING THE DATA
    insert_movie_ratings(MovielenseInserter(), movies)


def parse_data_from_source(parser):
    movies = parser.parse()
    file_handler.save_movies_json(movies, EXPORTS_FOLDER, JSON_FILE)
    sys.stdout.write('\r\n===== saved %i parsed movies from %s to %s/%s =====\r\n' %
                     (len(movies), type(parser.site).__name__, EXPORTS_FOLDER, JSON_FILE))
    sys.stdout.flush()
    return movies


def load_data_from_file(filename):
    movies = file_handler.load_movies_json(os.path.join(EXPORTS_FOLDER, filename))
    sys.stdout.write('\r\n===== loaded %i movies from %s/%s =====\r\n' % (len(movies), EXPORTS_FOLDER, filename))
    sys.stdout.flush()
    return movies


def insert_movie_ratings(inserter, movies):
    inserter.insert(movies)


if __name__ == "__main__":
    main()
