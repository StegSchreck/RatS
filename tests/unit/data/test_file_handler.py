import json
import os
from unittest import TestCase

from RatS.data import file_handler
from RatS.data.movie import Movie

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets', 'exports'))


class FileHandlerTest(TestCase):
    def setUp(self):
        self.movie = Movie()
        self.movie.title = 'Fight Club'
        self.movie.imdb.id = 'tt0137523'
        self.movie.imdb.url = 'http://www.imdb.com/title/tt0137523'
        self.movie.trakt.id = '432'
        self.movie.trakt.url = 'https://trakt.tv/movies/fight-club-1999'
        self.movie.trakt.my_rating = '10'
        self.movie.trakt.overall_rating = '89%'
        self.movie.tmdb.id = '550'
        self.movie.tmdb.url = 'https://www.themoviedb.org/movie/550'

    def test_load_movies_from_file(self):
        movies = file_handler.load_movies_json(os.path.join(TESTDATA_PATH, 'trakt.json'))
        self.assertEqual(1, len(movies))
        self.assertEqual(list, type(movies))
        self.assertEqual(Movie, type(movies[0]))
        self.assertEqual('Fight Club', movies[0].title)

    def test_save_empty_movies_to_file(self):
        movies = []
        filename = os.path.join(TESTDATA_PATH, 'TEST_empty_movies.json')
        file_handler.save_movies_json(movies, filename)
        with open(filename) as file:
            self.assertEqual(movies, json.load(file))
        os.remove(filename)

    def test_save_single_movie_to_file(self):
        movies = [self.movie]
        movies_json = [m.to_json() for m in movies]
        filename = os.path.join(TESTDATA_PATH, 'TEST_single_movie.json')
        file_handler.save_movies_json(movies, filename)
        with open(filename) as file:
            self.assertEqual(movies_json, json.load(file))
        os.remove(filename)

    def test_save_multiple_movies_to_file(self):
        movie2 = Movie()
        movie2.title = 'The Matrix'
        movie2.imdb.id = 'tt0133093'
        movie2.imdb.url = 'http://www.imdb.com/title/tt0133093'
        movie2.trakt.id = '481'
        movie2.trakt.url = 'https://trakt.tv/movies/the-matrix-1999'
        movie2.trakt.my_rating = '9'
        movie2.trakt.overall_rating = '89%'

        movies = [self.movie, movie2]
        movies_json = [m.to_json() for m in movies]
        filename = os.path.join(TESTDATA_PATH, 'TEST_multiple_movies.json')
        file_handler.save_movies_json(movies, filename)
        with open(filename) as file:
            self.assertEqual(movies_json, json.load(file))
        os.remove(filename)
