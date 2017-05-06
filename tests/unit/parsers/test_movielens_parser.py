import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.movielens_parser import MovielensRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MovielensParserTest(TestCase):

    def setUp(self):
        with open(os.path.join(TESTDATA_PATH, 'my_ratings', 'movielens.json'), encoding='utf8') as my_ratings:
            self.my_ratings = json.loads(my_ratings.read())

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        MovielensRatingsParser()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.parsers.movielens_parser.print_progress')
    @patch('RatS.parsers.movielens_parser.Movielens.get_json_from_html')
    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.movielens_parser.Movielens')
    def test_parser(self, site_mock, base_init_mock, browser_mock, json_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        json_mock.return_value = self.my_ratings
        parser = MovielensRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Movielense'
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(24, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Les Misérables', parser.movies[0]['title'])
        self.assertEqual(2012, parser.movies[0]['year'])

        self.assertEqual(99149, parser.movies[0]['movielens']['id'])
        self.assertEqual('https://movielens.org/movies/99149', parser.movies[0]['movielens']['url'])
        self.assertEqual(6, parser.movies[0]['movielens']['my_rating'])

        self.assertEqual('tt1707386', parser.movies[0]['imdb']['id'])
        self.assertEqual('http://www.imdb.com/title/tt1707386', parser.movies[0]['imdb']['url'])

        self.assertEqual(82695, parser.movies[0]['tmdb']['id'])
        self.assertEqual('https://www.themoviedb.org/movie/82695', parser.movies[0]['tmdb']['url'])
