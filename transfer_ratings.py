#!/usr/bin/env python
import argparse
import datetime
import os
import sys
import time
import traceback

from RatS.allocine.allocine_ratings_parser import AllocineRatingsParser
from RatS.criticker.criticker_ratings_inserter import CritickerRatingsInserter
from RatS.criticker.criticker_ratings_parser import CritickerRatingsParser
from RatS.filmaffinity.filmaffinity_ratings_inserter import FilmAffinityRatingsInserter
from RatS.filmaffinity.filmaffinity_ratings_parser import FilmAffinityRatingsParser
from RatS.icheckmovies.icheckmovies_misconfiguration_exception import ICheckMoviesMisconfigurationException
from RatS.icheckmovies.icheckmovies_ratings_inserter import ICheckMoviesRatingsInserter
from RatS.icheckmovies.icheckmovies_ratings_parser import ICheckMoviesRatingsParser
from RatS.imdb.imdb_ratings_inserter import IMDBRatingsInserter
from RatS.imdb.imdb_ratings_parser import IMDBRatingsParser
from RatS.letterboxd.letterboxd_ratings_inserter import LetterboxdRatingsInserter
from RatS.letterboxd.letterboxd_ratings_parser import LetterboxdRatingsParser
from RatS.listal.listal_ratings_inserter import ListalRatingsInserter
from RatS.listal.listal_ratings_parser import ListalRatingsParser
from RatS.metacritic.metacritic_ratings_inserter import MetacriticRatingsInserter
from RatS.movielens.movielens_ratings_inserter import MovielensRatingsInserter
from RatS.movielens.movielens_ratings_parser import MovielensRatingsParser
from RatS.moviepilot.moviepilot_ratings_inserter import MoviePilotRatingsInserter
from RatS.moviepilot.moviepilot_ratings_parser import MoviePilotRatingsParser
from RatS.plex.plex_ratings_inserter import PlexRatingsInserter
from RatS.plex.plex_ratings_parser import PlexRatingsParser
from RatS.rottentomatoes.rottentomatoes_ratings_inserter import RottenTomatoesRatingsInserter
from RatS.rottentomatoes.rottentomatoes_ratings_parser import RottenTomatoesRatingsParser
from RatS.tmdb.tmdb_ratings_inserter import TMDBRatingsInserter
from RatS.tmdb.tmdb_ratings_parser import TMDBRatingsParser
from RatS.trakt.trakt_ratings_inserter import TraktRatingsInserter
from RatS.trakt.trakt_ratings_parser import TraktRatingsParser
from RatS.utils import file_impex, command_line

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))

PARSERS = {
    'ALLOCINE': AllocineRatingsParser,
    'CRITICKER': CritickerRatingsParser,
    'FILMAFFINITY': FilmAffinityRatingsParser,
    # 'FLIXSTER': FlixsterRatingsParser,
    'ICHECKMOVIES': ICheckMoviesRatingsParser,
    'IMDB': IMDBRatingsParser,
    'LETTERBOXD': LetterboxdRatingsParser,
    'LISTAL': ListalRatingsParser,
    'MOVIELENS': MovielensRatingsParser,
    'MOVIEPILOT': MoviePilotRatingsParser,
    'PLEX': PlexRatingsParser,
    'ROTTENTOMATOES': RottenTomatoesRatingsParser,
    'TMDB': TMDBRatingsParser,
    'TRAKT': TraktRatingsParser,
}
INSERTERS = {
    'CRITICKER': CritickerRatingsInserter,
    'FILMAFFINITY': FilmAffinityRatingsInserter,
    # 'FLIXSTER': FlixsterRatingsInserter,
    'ICHECKMOVIES': ICheckMoviesRatingsInserter,
    'IMDB': IMDBRatingsInserter,
    'LETTERBOXD': LetterboxdRatingsInserter,
    'LISTAL': ListalRatingsInserter,
    'METACRITIC': MetacriticRatingsInserter,
    'MOVIELENS': MovielensRatingsInserter,
    'MOVIEPILOT': MoviePilotRatingsInserter,
    'PLEX': PlexRatingsInserter,
    'ROTTENTOMATOES': RottenTomatoesRatingsInserter,
    'TMDB': TMDBRatingsInserter,
    'TRAKT': TraktRatingsInserter,
}


def main():
    args = parse_args()
    try:
        execute(args)
    except ICheckMoviesMisconfigurationException as e:
        command_line.error(str(e))
        sys.exit(1)


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-s", "--source", help="Source of the movie ratings", required=True)
    argparser.add_argument("-d", "--destination", help="Destination for the ratings", required=False, action='append')
    argparser.add_argument("-D", "--all-destinations", help="Try to insert in all available destinations",
                           action="store_true")
    argparser.add_argument("-f", "--file", help="Import ratings from this file instead of parser "
                                                "(you still have provide the -s/--source argument "
                                                "to determine which data to use for inserting)", required=False)
    argparser.add_argument("-v", "--verbose", action="count", help="increase output verbosity", required=False)
    argparser.add_argument("-x", "--show_browser", help="show the browser doing his work",
                           action="store_true", required=False)
    args = argparser.parse_args()
    return args


def get_parser_from_arg(param):
    try:
        return PARSERS[param.upper()]
    except KeyError:
        command_line.error("No parser matching '{entered_parser}' found.".format(entered_parser=param))
        sys.stdout.write("Available parsers:\r\n")
        for parser in PARSERS:
            sys.stdout.write(' - {parser} \n'.format(parser=parser))
        sys.stdout.flush()
        sys.exit(1)


def get_inserter_from_arg(param):
    try:
        return INSERTERS[param.upper()]
    except KeyError:
        command_line.error("No inserter matching '{entered_inserter}' found.".format(entered_inserter=param))
        sys.stdout.write("Available inserters:\r\n")
        for inserter in INSERTERS:
            sys.stdout.write(' - {inserter} \n'.format(inserter=inserter))
        sys.stdout.flush()
        sys.exit(1)


def execute(args):
    parser = get_parser_from_arg(args.source)(args)
    movies = execute_parsing(args, parser)
    execute_inserting(args, movies, parser)


def execute_inserting(args, movies, parser):
    destinations = list(INSERTERS.keys()) if args.all_destinations \
        else [destination.upper() for destination in args.destination]
    _filter_source_site_from_destinations(destinations, parser.site.site_name)
    if destinations:
        if len(movies) == 0:
            command_line.error("There are no files to be inserted. Did the parser run properly?")
            sys.exit(1)
        # INSERT THE DATA
        for destination in destinations:
            inserter = get_inserter_from_arg(destination)(args)
            insert_movie_ratings(inserter, movies, type(parser.site).__name__)


def _filter_source_site_from_destinations(destinations, parser_site_name):
    if parser_site_name.upper() in destinations:
        destinations.remove(parser_site_name.upper())
        command_line.info("Will not insert ratings to their source. Skipping {site_name}.".format(
            site_name=parser_site_name
        ))


def execute_parsing(args, parser):
    if not parser.site.CREDENTIALS_VALID:
        command_line.error("No valid credentials found for {site_name}. Skipping parsing.".format(
            site_name=parser.site.site_name
        ))
        sys.exit(1)
    if args.file:
        # LOAD FROM FILE
        movies = load_data_from_file(args.file)
        parser.site.browser_handler.kill()
    else:
        # PARSE DATA
        movies = parse_data_from_source(parser)
    return movies


def parse_data_from_source(parser):
    movies = parser.parse()
    json_filename = '{timestamp}_{sitename}.json'.format(timestamp=TIMESTAMP, sitename=type(parser.site).__name__)
    file_impex.save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename=json_filename)
    sys.stdout.write('\r\n===== {site_displayname}: saved {parsed_movies_count} parsed movies to '
                     '{folder}/{filename}\r\n'.format(
                         site_displayname=parser.site.site_displayname,
                         parsed_movies_count=len(movies),
                         folder=EXPORTS_FOLDER,
                         filename=json_filename
                     ))
    sys.stdout.flush()
    return movies


def load_data_from_file(filename):
    movies = file_impex.load_movies_from_json(folder=EXPORTS_FOLDER, filename=filename)
    sys.stdout.write('\r\n===== loaded {loaded_movies_count} movies from {folder}/{filename}\r\n'.format(
        loaded_movies_count=len(movies),
        folder=EXPORTS_FOLDER,
        filename=filename
    ))
    sys.stdout.flush()
    return movies


def insert_movie_ratings(inserter, movies, source):
    if inserter.site.CREDENTIALS_VALID:
        try:
            inserter.insert(movies, source)
        except Exception:  # pylint: disable=broad-except
            # exception should be logged in a file --> issue #15
            sys.stdout.flush()
            inserter.site.browser_handler.kill()
            command_line.error("There was an exception inside {site_name} (see below). Skipping insertion.".format(
                site_name=inserter.site.site_name
            ))
            traceback.print_exc()
    else:
        command_line.warn("No valid credentials found for {site_name}. Skipping insertion.".format(
            site_name=inserter.site.site_name
        ))


if __name__ == "__main__":
    main()
