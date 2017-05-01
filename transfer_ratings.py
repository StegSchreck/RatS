#!/usr/bin/env python
import datetime
import os
import sys
import time

from RatS.inserters.criticker_inserter import CritickerInserter
from RatS.inserters.imdb_inserter import IMDBInserter
from RatS.inserters.letterboxd_uploader import LetterboxdUploader
from RatS.inserters.listal_inserter import ListalInserter
from RatS.inserters.movielens_inserter import MovielensInserter
from RatS.inserters.tmdb_uploader import TMDBUploader
from RatS.inserters.trakt_inserter import TraktInserter
from RatS.parsers.criticker_parser import CritickerRatingsParser
from RatS.parsers.imdb_parser import IMDBRatingsParser
from RatS.parsers.listal_parser import ListalRatingsParser
from RatS.parsers.movielens_parser import MovielensRatingsParser
from RatS.parsers.tmdb_parser import TMDBRatingsParser
from RatS.parsers.trakt_parser import TraktRatingsParser
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))

PARSERS = {
    'TRAKT': TraktRatingsParser,
    'IMDB': IMDBRatingsParser,
    'MOVIELENS': MovielensRatingsParser,
    'TMDB': TMDBRatingsParser,
    'LISTAL': ListalRatingsParser,
    'CRITICKER': CritickerRatingsParser,
}
INSERTERS = {
    'IMDB': IMDBInserter,
    'MOVIELENS': MovielensInserter,
    'TRAKT': TraktInserter,
    'TMDB': TMDBUploader,
    'LISTAL': ListalInserter,
    'CRITICKER': CritickerInserter,
    'LETTERBOXD': LetterboxdUploader,
}


def main(argv):
    if len(argv) != 3:
        print_help(argv)
        return
    if argv[1].upper() not in PARSERS:
        sys.stdout.write("No parser matching '%s' found.\r\nAvailable parsers:\r\n" % argv[1])
        for parser in PARSERS:
            sys.stdout.write(' - %s \n' % parser)
        sys.stdout.flush()
        return
    if argv[2].upper() not in INSERTERS:
        sys.stdout.write("No inserter matching '%s' found.\r\nAvailable inserters:\r\n" % argv[2])
        for inserter in INSERTERS:
            sys.stdout.write(' - %s \n' % inserter)
        sys.stdout.flush()
        return

    execute(argv)


def print_help(argv):
    sys.stdout.write('''\r\nThe number of arguments was not correct!
        \r\nExample call:
        \r\n   python %s imdb movielens
        \r\nThis would parse your ratings from IMDB and insert them to your Movielens account
        \r\n''' % argv[0])
    sys.stdout.flush()


def get_parser_from_arg(param):
    try:
        return PARSERS[param.upper()]
    except KeyError:
        return None


def get_inserter_from_arg(param):
    try:
        return INSERTERS[param.upper()]
    except KeyError:
        return None


def execute(argv):
    # PARSING DATA
    parser = get_parser_from_arg(argv[1])()
    movies = parse_data_from_source(parser)
    # FILE LOADING
    # movies = load_data_from_file(filename)
    # POSTING THE DATA
    inserter = get_inserter_from_arg(argv[2])()
    insert_movie_ratings(inserter, movies, type(parser.site).__name__)


def parse_data_from_source(parser):
    movies = parser.parse()
    json_filename = '%s_%s.json' % (TIMESTAMP, type(parser.site).__name__)
    file_impex.save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename=json_filename)
    sys.stdout.write('\r\n===== %s: saved %i parsed movies to %s/%s\r\n' %
                     (type(parser.site).__name__, len(movies), EXPORTS_FOLDER, json_filename))
    sys.stdout.flush()
    return movies


def load_data_from_file(filename):
    movies = file_impex.load_movies_from_json(folder=EXPORTS_FOLDER, filename=filename)
    sys.stdout.write('\r\n===== loaded %i movies from %s/%s\r\n' % (len(movies), EXPORTS_FOLDER, filename))
    sys.stdout.flush()
    return movies


def insert_movie_ratings(inserter, movies, source):
    inserter.insert(movies, source)


if __name__ == "__main__":
    main(sys.argv)
