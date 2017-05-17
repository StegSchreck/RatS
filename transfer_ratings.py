#!/usr/bin/env python
import argparse
import datetime
import os
import sys
import time

from RatS.inserters.criticker_inserter import CritickerInserter
from RatS.inserters.flixster_inserter import FlixsterInserter
from RatS.inserters.imdb_inserter import IMDBInserter
from RatS.inserters.letterboxd_uploader import LetterboxdUploader
from RatS.inserters.listal_inserter import ListalInserter
from RatS.inserters.movielens_uploader import MovielensUploader
from RatS.inserters.tmdb_uploader import TMDBUploader
from RatS.inserters.trakt_inserter import TraktInserter
from RatS.parsers.criticker_parser import CritickerRatingsParser
from RatS.parsers.flixster_parser import FlixsterRatingsParser
from RatS.parsers.imdb_parser import IMDBRatingsParser
from RatS.parsers.letterboxd_parser import LetterboxdRatingsParser
from RatS.parsers.listal_parser import ListalRatingsParser
from RatS.parsers.movielens_parser import MovielensRatingsParser
from RatS.parsers.tmdb_parser import TMDBRatingsParser
from RatS.parsers.trakt_parser import TraktRatingsParser
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))

PARSERS = {
    'CRITICKER': CritickerRatingsParser,
    'FLIXSTER': FlixsterRatingsParser,
    'IMDB': IMDBRatingsParser,
    'LETTERBOXD': LetterboxdRatingsParser,
    'LISTAL': ListalRatingsParser,
    'MOVIELENS': MovielensRatingsParser,
    'TMDB': TMDBRatingsParser,
    'TRAKT': TraktRatingsParser,
}
INSERTERS = {
    'CRITICKER': CritickerInserter,
    'FLIXSTER': FlixsterInserter,
    'IMDB': IMDBInserter,
    'LETTERBOXD': LetterboxdUploader,
    'LISTAL': ListalInserter,
    'MOVIELENS': MovielensUploader,
    'TMDB': TMDBUploader,
    'TRAKT': TraktInserter,
}


def main():
    args = parse_args()
    execute(args)


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-s", "--source", help="Source of the movie ratings", required=True)
    argparser.add_argument("-d", "--destination", help="Destination for the ratings", required=True)
    args = argparser.parse_args()
    return args


def get_parser_from_arg(param):
    try:
        return PARSERS[param.upper()]
    except KeyError:
        sys.stdout.write("No parser matching '%s' found.\r\nAvailable parsers:\r\n" % args.source)
        for parser in PARSERS:
            sys.stdout.write(' - %s \n' % parser)
        sys.stdout.flush()
        sys.exit(1)


def get_inserter_from_arg(param):
    try:
        return INSERTERS[param.upper()]
    except KeyError:
        sys.stdout.write("No inserter matching '%s' found.\r\nAvailable inserters:\r\n" % args.destination)
        for inserter in INSERTERS:
            sys.stdout.write(' - %s \n' % inserter)
        sys.stdout.flush()
        sys.exit(1)


def execute(args):
    # PARSING DATA
    parser = get_parser_from_arg(args.source)()
    movies = parse_data_from_source(parser)
    # FILE LOADING
    # movies = load_data_from_file(filename)
    # POSTING THE DATA
    inserter = get_inserter_from_arg(args.destination)()
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
    main()
