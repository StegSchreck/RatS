#!/usr/bin/env python
import csv
import json
import os

from data.movie import Movie
from parsers.trakt_parser import TraktRatingsParser

EXPORTS_FOLDER = os.path.dirname(__file__) + 'exports/'
TRAKT_JSON_FILE = os.path.join(EXPORTS_FOLDER, 'trakt.json')
TRAKT_CSV_FILE = os.path.join(EXPORTS_FOLDER, 'trakt.csv')


def load_movies_json(filename):
    with open(filename) as file:
        movies_json = json.load(file)
        file.close()
        return [Movie.from_json(movie) for movie in movies_json]


def save_movies_json(movies_to_save, filename):
    with open(filename, 'w') as file:
        movies_json = [movie.to_json() for movie in movies_to_save]
        file.write(json.dumps(movies_json))
        file.close()


def save_movies_to_csv(movies_to_save, filename):
    movies_json = [movie.to_json() for movie in movies_to_save]
    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'imdb', 'trakt', 'tmdb', 'movielense', 'rottentomato'])
        writer.writeheader()
        writer.writerows(movies_json)
        file.close()


if __name__ == "__main__":
    #trakt_parser = TraktRatingsParser()
    #movies = trakt_parser.parse()
    #save_movies_json(movies, TRAKT_JSON_FILE)
    loaded_movies = load_movies_json(TRAKT_JSON_FILE)
    #save_movies_to_csv(loaded_movies, TRAKT_CSV_FILE)

