#!/usr/bin/env python
import argparse
import datetime
import logging
import os
import sys
import time
import traceback
from importlib import reload
from typing import Mapping

from RatS.allocine.allocine_ratings_inserter import AlloCineRatingsInserter
from RatS.allocine.allocine_ratings_parser import AlloCineRatingsParser
from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.movie_entity import Site, Movie
from RatS.base.base_exceptions import (
    RatSException,
    NoMoviesForInsertion,
    NoValidCredentialsException,
)
from RatS.criticker.criticker_ratings_inserter import CritickerRatingsInserter
from RatS.criticker.criticker_ratings_parser import CritickerRatingsParser
from RatS.filmaffinity.filmaffinity_ratings_inserter import FilmAffinityRatingsInserter
from RatS.filmaffinity.filmaffinity_ratings_parser import FilmAffinityRatingsParser
from RatS.filmtipset.filmtipset_ratings_inserter import FilmtipsetRatingsInserter
from RatS.filmtipset.filmtipset_ratings_parser import FilmtipsetRatingsParser
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
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "RatS", "exports"))

PARSERS: Mapping[Site, RatingsParser] = {
    Site.ALLOCINE: AlloCineRatingsParser,
    Site.CRITICKER: CritickerRatingsParser,
    Site.FILMAFFINITY: FilmAffinityRatingsParser,
    Site.FILMTIPSET: FilmtipsetRatingsParser,
    # Site.FLIXSTER: FlixsterRatingsParser,
    Site.ICHECKMOVIES: ICheckMoviesRatingsParser,
    Site.IMDB: IMDBRatingsParser,
    Site.LETTERBOXD: LetterboxdRatingsParser,
    Site.LISTAL: ListalRatingsParser,
    Site.MOVIELENS: MovielensRatingsParser,
    Site.MOVIEPILOT: MoviePilotRatingsParser,
    Site.PLEX: PlexRatingsParser,
    Site.ROTTENTOMATOES: RottenTomatoesRatingsParser,
    Site.TMDB: TMDBRatingsParser,
    Site.TRAKT: TraktRatingsParser,
}
INSERTERS: Mapping[Site, RatingsInserter] = {
    Site.ALLOCINE: AlloCineRatingsInserter,
    Site.CRITICKER: CritickerRatingsInserter,
    Site.FILMAFFINITY: FilmAffinityRatingsInserter,
    Site.FILMTIPSET: FilmtipsetRatingsInserter,
    # Site.FLIXSTER: FlixsterRatingsInserter,
    Site.ICHECKMOVIES: ICheckMoviesRatingsInserter,
    Site.IMDB: IMDBRatingsInserter,
    Site.LETTERBOXD: LetterboxdRatingsInserter,
    Site.LISTAL: ListalRatingsInserter,
    Site.METACRITIC: MetacriticRatingsInserter,
    Site.MOVIELENS: MovielensRatingsInserter,
    Site.MOVIEPILOT: MoviePilotRatingsInserter,
    Site.PLEX: PlexRatingsInserter,
    Site.ROTTENTOMATOES: RottenTomatoesRatingsInserter,
    Site.TMDB: TMDBRatingsInserter,
    Site.TRAKT: TraktRatingsInserter,
}


def main():
    args = parse_args()
    init_logging(args)
    try:
        execute(args)
    except RatSException as e:
        logging.error(str(e))
        sys.exit(1)


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-s",
        "--source",
        help="Source of the movie ratings",
        required=True,
    )
    argparser.add_argument(
        "-d",
        "--destination",
        help="Destination for the ratings",
        required=False,
        action="append",
    )
    argparser.add_argument(
        "-D",
        "--all-destinations",
        help="Try to insert in all available destinations",
        type=bool,
        action="store_true",
    )
    argparser.add_argument(
        "-f",
        "--file",
        help="Import ratings from this file instead of parser "
        "(you still have provide the -s/--source argument "
        "to determine which data to use for inserting)",
        type=str,
        required=False,
    )
    argparser.add_argument(
        "--log",
        help="log level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        required=False,
    )
    argparser.add_argument(
        "-x",
        "--show_browser",
        help="show the browser doing his work",
        type=bool,
        action="store_true",
        required=False,
    )
    args = argparser.parse_args()
    return args


def get_parser_from_arg(site: Site) -> RatingsParser:
    try:
        return PARSERS.get(site)
    except (KeyError, ValueError):
        logging.error(f"No parser matching '{site.name}' found.")
        logging.info(f"Available parsers: {[parser for parser in PARSERS]}")
        sys.exit(1)


def get_inserter_from_arg(site: Site) -> RatingsInserter:
    try:
        return INSERTERS.get(site)
    except (KeyError, ValueError):
        logging.error(f"No inserter matching '{site.name}' found.")
        logging.info(f"Available inserters: {[inserter for inserter in INSERTERS]}")
        sys.exit(1)


def init_logging(args):
    log_level = getattr(logging, args.log.upper(), None)
    reload(logging)
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def execute(args):
    try:
        site: Site = Site(args.source.upper())
        parser: RatingsParser = get_parser_from_arg(site)(args)
        movies: list[Movie] = execute_parsing(args, parser)
        execute_inserting(args, movies, parser)
    except RatSException as e:
        logging.error(str(e))


def execute_inserting(args, movies: list[Movie], parser: RatingsParser):
    if not args.all_destinations and not args.destination:
        return
    destinations: list[Site] = (
        [inserter for inserter in INSERTERS.keys()]
        if args.all_destinations
        else [Site(destination.upper()) for destination in args.destination]
    )
    _filter_source_site_from_destinations(destinations, parser.site.site_name)
    if destinations:
        if len(movies) == 0:
            NoMoviesForInsertion("There are no files to be inserted. Did the parser run properly?")
        # INSERT THE DATA
        for destination in destinations:
            try:
                inserter: RatingsInserter = get_inserter_from_arg(destination)(args)
                insert_movie_ratings(inserter, movies, parser.site.site)
            except RatSException as e:
                logging.error(str(e))


def _filter_source_site_from_destinations(destinations: list[str], parser_site_name: str):
    if parser_site_name.upper() in destinations:
        destinations.remove(parser_site_name.upper())
        logging.warning(f"Will not insert ratings to their source. Skipping {parser_site_name}.")


def execute_parsing(args, parser: RatingsParser) -> list[Movie]:
    if not parser.site.CREDENTIALS_VALID:
        raise NoValidCredentialsException(f"No valid credentials found for {parser.site.site_name}. Skipping parsing.")
    if args.file:
        # LOAD FROM FILE
        movies: list[Movie] = load_data_from_file(args.file)
        parser.site.browser_handler.kill()
    else:
        # PARSE DATA
        movies: list[Movie] = parse_data_from_source(parser)
    return movies


def parse_data_from_source(parser: RatingsParser) -> list[Movie]:
    try:
        movies: list[Movie] = parser.parse()
    except RatSException as e:
        logging.error(str(e))
        sys.exit(1)

    json_filename: str = f"{TIMESTAMP}_{type(parser.site).__name__}.json"
    file_impex.save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename=json_filename)
    logging.info(
        f"===== {parser.site.site_name}: saved {len(movies)} parsed movies to {EXPORTS_FOLDER}/{json_filename}"
    )
    return movies


def load_data_from_file(filename: str) -> list[Movie]:
    movies: list[Movie] = file_impex.load_movies_from_json(folder=EXPORTS_FOLDER, filename=filename)
    logging.info(f"===== loaded {len(movies)} movies from {EXPORTS_FOLDER}/{filename}")
    return movies


def insert_movie_ratings(inserter: RatingsInserter, movies: list[Movie], source: Site):
    if inserter.site.CREDENTIALS_VALID:
        try:
            inserter.insert(movies, source)
        except RatSException as e:
            logging.error(str(e))
        except Exception:  # pylint: disable=broad-except
            inserter.site.browser_handler.kill()
            logging.error(f"There was an exception inside {inserter.site.site_name} (see below). - Skipping insertion.")
            traceback.print_exc()
    else:
        logging.warning(f"No valid credentials found for {inserter.site.site_name}. Skipping insertion.")


if __name__ == "__main__":
    main()
