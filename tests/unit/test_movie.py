import json
import os
from unittest import TestCase

from data.movie import Movie

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'assets', 'exports'))


class MovieTest(TestCase):
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

    def test_equals(self):
        movie2 = Movie()
        movie2.title = 'Fight Club'
        movie2.imdb.id = 'tt0137523'
        movie2.imdb.url = 'http://www.imdb.com/title/tt0137523'
        movie2.trakt.id = '432'
        movie2.trakt.url = 'https://trakt.tv/movies/fight-club-1999'
        movie2.trakt.my_rating = '10'
        movie2.trakt.overall_rating = '89%'
        movie2.tmdb.id = '550'
        movie2.tmdb.url = 'https://www.themoviedb.org/movie/550'
        self.assertEqual(self.movie, movie2)

    def test_not_equals_title(self):
        movie2 = Movie()
        movie2.title = 'The Matrix'
        movie2.imdb.id = 'tt0137523'
        movie2.imdb.url = 'http://www.imdb.com/title/tt0137523'
        movie2.trakt.id = '432'
        movie2.trakt.url = 'https://trakt.tv/movies/fight-club-1999'
        movie2.trakt.my_rating = '10'
        movie2.trakt.overall_rating = '89%'
        movie2.tmdb.id = '550'
        movie2.tmdb.url = 'https://www.themoviedb.org/movie/550'
        self.assertNotEqual(self.movie, movie2)

    def test_not_equals_imdb(self):
        movie2 = Movie()
        movie2.title = 'Fight Club'
        movie2.imdb.id = 'XYZ'
        movie2.imdb.url = 'http://www.imdb.com/title/tt0137523'
        movie2.trakt.id = '432'
        movie2.trakt.url = 'https://trakt.tv/movies/fight-club-1999'
        movie2.trakt.my_rating = '10'
        movie2.trakt.overall_rating = '89%'
        movie2.tmdb.id = '550'
        movie2.tmdb.url = 'https://www.themoviedb.org/movie/550'
        self.assertNotEqual(self.movie, movie2)

    def test_json_serializing(self):
        movie_json = self.movie.to_json()
        with open(os.path.join(TESTDATA_PATH, 'trakt.json'), encoding='utf8') as json_file:
            movie_json_from_file = json.load(json_file)[0]
            self.assertEqual(movie_json_from_file, movie_json)

    def test_json_deserializing(self):
        with open(os.path.join(TESTDATA_PATH, 'trakt.json'), encoding='utf8') as json_file:
            movie_from_json = self.movie.from_json(json.load(json_file)[0])
            self.assertEqual(self.movie, movie_from_json)
