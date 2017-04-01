import csv
import datetime
import json
import os
import time
from unittest import TestCase

from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))
TESTDATA_NEW_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets', TIMESTAMP))


class FileHandlerTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['year'] = 1999
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['imdb']['my_rating'] = 10
        self.movie['trakt'] = dict()
        self.movie['trakt']['id'] = '432'
        self.movie['trakt']['url'] = 'https://trakt.tv/movies/fight-club-1999'
        self.movie['trakt']['my_rating'] = 10
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'

    def test_load_movies_from_json(self):
        movies = file_impex.load_movies_from_json(folder=os.path.join(TESTDATA_PATH, 'exports'), filename='trakt.json')
        self.assertEqual(1, len(movies))
        self.assertEqual(list, type(movies))
        self.assertEqual(dict, type(movies[0]))
        self.assertEqual('Fight Club', movies[0]['title'])

    def test_save_empty_movies_to_json(self):
        movies = []
        filename = os.path.join(os.path.join(TESTDATA_PATH, 'exports'), 'TEST_empty_movies.json')
        file_impex.save_movies_to_json(movies, os.path.join(TESTDATA_PATH, 'exports'), 'TEST_empty_movies.json')
        with open(filename) as file:
            self.assertEqual(movies, json.load(file))
        os.remove(filename)

    def test_save_empty_movies_to_json_in_new_folder(self):
        movies = []
        filename = os.path.join(TESTDATA_NEW_PATH, 'TEST_empty_movies.json')
        file_impex.save_movies_to_json(movies, TESTDATA_NEW_PATH, 'TEST_empty_movies.json')
        with open(filename) as file:
            self.assertEqual(movies, json.load(file))
        os.remove(filename)
        os.removedirs(TESTDATA_NEW_PATH)

    def test_save_single_movie_to_json(self):
        movies = [self.movie]
        movies_json = [m for m in movies]
        filename = os.path.join(os.path.join(TESTDATA_PATH, 'exports'), 'TEST_single_movie.json')
        file_impex.save_movies_to_json(movies, os.path.join(TESTDATA_PATH, 'exports'), 'TEST_single_movie.json')
        with open(filename) as file:
            self.assertEqual(movies_json, json.load(file))
        os.remove(filename)

    def test_save_multiple_movies_to_json(self):
        movie2 = dict()
        movie2['title'] = 'The Matrix'
        movie2['year'] = 1999
        movie2['imdb'] = dict()
        movie2['imdb']['id'] = 'tt0133093'
        movie2['imdb']['url'] = 'http://www.imdb.com/title/tt0133093'
        movie2['trakt'] = dict()
        movie2['trakt']['id'] = '481'
        movie2['trakt']['url'] = 'https://trakt.tv/movies/the-matrix-1999'
        movie2['trakt']['my_rating'] = 9

        movies = [self.movie, movie2]
        movies_json = movies
        filename = os.path.join(os.path.join(TESTDATA_PATH, 'exports'), 'TEST_multiple_movies.json')
        file_impex.save_movies_to_json(movies, os.path.join(TESTDATA_PATH, 'exports'), 'TEST_multiple_movies.json')
        with open(filename) as file:
            self.assertEqual(movies_json, json.load(file))
        os.remove(filename)

    def test_load_movies_from_csv(self):
        parsed_movies = file_impex.load_movies_from_csv(os.path.join(TESTDATA_PATH, 'my_ratings', 'imdb.csv'))

        self.assertEqual(2, len(parsed_movies))
        self.assertEqual(dict, type(parsed_movies[0]))
        self.assertEqual('Arrival', parsed_movies[0]['title'])
        self.assertEqual('2016', parsed_movies[0]['year'])
        self.assertEqual('tt2543164', parsed_movies[0]['imdb']['id'])
        self.assertEqual('http://www.imdb.com/title/tt2543164/', parsed_movies[0]['imdb']['url'])
        self.assertEqual(8, parsed_movies[0]['imdb']['my_rating'])

    def test_save_single_movie_to_csv(self):
        movies = [self.movie]
        filename = os.path.join(os.path.join(TESTDATA_PATH, 'exports'), 'TEST_single_movie.csv')
        file_impex.save_movies_to_csv(movies, os.path.join(TESTDATA_PATH, 'exports'),
                                      'TEST_single_movie.csv',
                                      'imdb')
        with open(filename) as file:
            reader = csv.reader(file, delimiter=',')
            next(reader)  # csv header
            row = next(reader)
            self.assertEqual(self.movie['title'], row[5])
            self.assertEqual(self.movie['year'], int(row[11]))
            self.assertEqual(self.movie['imdb']['id'], row[1])
            self.assertEqual(self.movie['imdb']['url'], row[15])
            self.assertEqual(self.movie['imdb']['my_rating'], int(row[8]))
        os.remove(filename)

    def test_save_multiple_movies_to_csv(self):
        movie2 = dict()
        movie2['title'] = 'Star Trek - Der Film'
        movie2['year'] = 1979
        movie2['imdb'] = dict()
        movie2['imdb']['id'] = 'tt0079945'
        movie2['imdb']['url'] = 'http://www.imdb.com/title/tt0079945'
        movie2['trakt'] = dict()
        movie2['trakt']['id'] = '117'
        movie2['trakt']['url'] = 'https://trakt.tv/movies/star-trek-the-motion-picture-1979'
        movie2['trakt']['my_rating'] = 8

        movies = [self.movie, movie2]
        filename = os.path.join(os.path.join(TESTDATA_PATH, 'exports'), 'TEST_multiple_movies.csv')
        file_impex.save_movies_to_csv(movies, os.path.join(TESTDATA_PATH, 'exports'),
                                      'TEST_multiple_movies.csv',
                                      'trakt')
        with open(filename) as file:
            reader = csv.reader(file, delimiter=',')
            next(reader)  # csv header
            row1 = next(reader)
            self.assertEqual(self.movie['title'], row1[5])
            self.assertEqual(self.movie['year'], int(row1[11]))
            self.assertEqual(self.movie['imdb']['id'], row1[1])
            self.assertEqual(self.movie['imdb']['url'], row1[15])
            self.assertEqual(self.movie['trakt']['my_rating'], int(row1[8]))
            row2 = next(reader)
            self.assertEqual(movie2['title'], row2[5])
            self.assertEqual(movie2['year'], int(row2[11]))
            self.assertEqual(movie2['imdb']['id'], row2[1])
            self.assertEqual(movie2['imdb']['url'], row2[15])
            self.assertEqual(movie2['trakt']['my_rating'], int(row2[8]))
        os.remove(filename)
