import json
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel


class Site(str, Enum):
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


class SiteSpecificMovieData(BaseModel):
    id: Optional[str]
    url: Optional[str]
    my_rating: Optional[int]  # 1 - 10
    # average_rating: float  # 1.0 - 10.0

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return self.__str__()

    @staticmethod
    def from_json(json_dct):
        data = SiteSpecificMovieData(id=json_dct["id"], url=json_dct["url"])
        if "my_rating" in json_dct:
            data.my_rating = json_dct["my_rating"]
        return data


class Movie(BaseModel):
    title: Optional[str]
    year: Optional[int]
    site_data: Dict[Site, SiteSpecificMovieData] = dict()

    def __str__(self):
        return json.dumps(self.to_json())

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        to_return = {"title": self.title, "year": self.year}
        site_data = {}
        for key, site_specific_movie_data in self.site_data.items():
            site_data[key] = site_specific_movie_data.to_json()

        to_return["siteData"] = site_data
        return to_return

    @staticmethod
    def from_json(json_dct):
        if "id" in json_dct.keys():
            return SiteSpecificMovieData.from_json(json_dct)
        elif "siteData" in json_dct.keys():
            return Movie(
                title=json_dct["title"],
                year=json_dct["year"] if "year" in json_dct else None,
            )
        else:
            return json_dct
