from enum import Enum
from typing import List, Optional, Dict


class Site(Enum):
    ALLOCINE = "ALLOCINE"
    CRITICKER = "CRITICKER"
    FILMAFFINITY = "FILMAFFINITY"
    FILMTIPSET = "FILMTIPSET"
    FLIXSTER = "FLIXSTER"
    ICHECKMOVIES = "ICHECKMOVIES"
    IMDB = "IMDB"
    LETTERBOXD = "LETTERBOXD"
    LISTAL = "LISTAL"
    METACRITIC = "METACRITIC"
    MOVIELENS = "MOVIELENS"
    MOVIEPILOT = "MOVIEPILOT"
    PLEX = "PLEX"
    ROTTENTOMATOES = "ROTTENTOMATOES"
    TMDB = "TMDB"
    TRAKT = "TRAKT"


class SiteSpecificMovieData:
    id: str
    url: str
    my_rating: int  # 1 - 10
    # average_rating: float  # 1.0 - 10.0


class Movie:
    title: str
    year: Optional[int]
    site_data: Dict[Site, SiteSpecificMovieData] = dict()
