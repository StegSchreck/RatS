import datetime
import json
import os
import time
from unittest import TestCase

from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets', 'exports'))
TESTDATA_NEW_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets', TIMESTAMP))


class FileHandlerTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['trakt'] = dict()
        self.movie['trakt']['id'] = '432'
        self.movie['trakt']['url'] = 'https://trakt.tv/movies/fight-club-1999'
        self.movie['trakt']['my_rating'] = '10'
        self.movie['trakt']['overall_rating'] = '89%'
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'

    def test_load_movies_from_file(self):
        movies = file_impex.load_movies_json(folder=TESTDATA_PATH, filename='trakt.json')
        self.assertEqual(1, len(movies))
        self.assertEqual(list, type(movies))
        self.assertEqual(dict, type(movies[0]))
        self.assertEqual('Fight Club', movies[0]['title'])

    def test_save_empty_movies_to_file(self):
        movies = []
        filename = os.path.join(TESTDATA_PATH, 'TEST_empty_movies.json')
        file_impex.save_movies_json(movies, TESTDATA_PATH, 'TEST_empty_movies.json')
        with open(filename) as file:
            self.assertEqual(movies, json.load(file))
        os.remove(filename)

    def test_save_empty_movies_to_file_in_new_folder(self):
        movies = []
        filename = os.path.join(TESTDATA_NEW_PATH, 'TEST_empty_movies.json')
        file_impex.save_movies_json(movies, TESTDATA_NEW_PATH, 'TEST_empty_movies.json')
        with open(filename) as file:
            self.assertEqual(movies, json.load(file))
        os.remove(filename)
        os.removedirs(TESTDATA_NEW_PATH)

    def test_save_single_movie_to_file(self):
        movies = [self.movie]
        movies_json = [m for m in movies]
        filename = os.path.join(TESTDATA_PATH, 'TEST_single_movie.json')
        file_impex.save_movies_json(movies, TESTDATA_PATH, 'TEST_single_movie.json')
        with open(filename) as file:
            self.assertEqual(movies_json, json.load(file))
        os.remove(filename)

    def test_save_multiple_movies_to_file(self):
        movie2 = dict()
        movie2['title'] = 'The Matrix'
        movie2['imdb'] = dict()
        movie2['imdb']['id'] = 'tt0133093'
        movie2['imdb']['url'] = 'http://www.imdb.com/title/tt0133093'
        movie2['trakt'] = dict()
        movie2['trakt']['id'] = '481'
        movie2['trakt']['url'] = 'https://trakt.tv/movies/the-matrix-1999'
        movie2['trakt']['my_rating'] = '9'
        movie2['trakt']['overall_rating'] = '89%'

        movies = [self.movie, movie2]
        movies_json = movies
        filename = os.path.join(TESTDATA_PATH, 'TEST_multiple_movies.json')
        file_impex.save_movies_json(movies, TESTDATA_PATH, 'TEST_multiple_movies.json')
        with open(filename) as file:
            self.assertEqual(movies_json, json.load(file))
        os.remove(filename)
