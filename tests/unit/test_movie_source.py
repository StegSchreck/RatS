import json
import os
from unittest import TestCase

from data.movie_source import MovieSource

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'assets', 'exports'))


class MovieSourceTest(TestCase):
    def setUp(self):
        self.movie_source = MovieSource()
        self.movie_source.id = '432'
        self.movie_source.url = 'https://trakt.tv/movies/fight-club-1999'
        self.movie_source.my_rating = '10'
        self.movie_source.overall_rating = '89%'

    def test_equals(self):
        movie_source2 = MovieSource()
        movie_source2.id = '432'
        movie_source2.url = 'https://trakt.tv/movies/fight-club-1999'
        movie_source2.my_rating = '10'
        movie_source2.overall_rating = '89%'
        self.assertEqual(self.movie_source, movie_source2)

    def test_not_equals_id(self):
        movie_source2 = MovieSource()
        movie_source2.id = '666'
        movie_source2.url = 'https://trakt.tv/movies/fight-club-1999'
        movie_source2.my_rating = '10'
        movie_source2.overall_rating = '89%'
        self.assertNotEqual(self.movie_source, movie_source2)

    def test_not_equals_url(self):
        movie_source2 = MovieSource()
        movie_source2.id = '432'
        movie_source2.url = 'https://trakt.tv/movies/somewhere/else'
        movie_source2.my_rating = '10'
        movie_source2.overall_rating = '89%'
        self.assertNotEqual(self.movie_source, movie_source2)

    def test_not_equals_my_rating(self):
        movie_source2 = MovieSource()
        movie_source2.id = '432'
        movie_source2.url = 'https://trakt.tv/movies/fight-club-1999'
        movie_source2.my_rating = '8'
        movie_source2.overall_rating = '89%'
        self.assertNotEqual(self.movie_source, movie_source2)

    def test_not_equals_overall_rating(self):
        movie_source2 = MovieSource()
        movie_source2.id = '432'
        movie_source2.url = 'https://trakt.tv/movies/fight-club-1999'
        movie_source2.my_rating = '10'
        movie_source2.overall_rating = '95%'
        self.assertNotEqual(self.movie_source, movie_source2)

    def test_json_serializing(self):
        movie_source_json = self.movie_source.to_json()
        with open(os.path.join(TESTDATA_PATH, 'trakt.json'), encoding='utf8') as json_file:
            movie_source_json_from_file = json.load(json_file)[0]['trakt']
            self.assertEqual(movie_source_json_from_file, movie_source_json)

    def test_json_deserializing(self):
        with open(os.path.join(TESTDATA_PATH, 'trakt.json'), encoding='utf8') as json_file:
            movie_source_from_json = self.movie_source.from_json(json.load(json_file)[0]['trakt'])
            self.assertEqual(self.movie_source, movie_source_from_json)
