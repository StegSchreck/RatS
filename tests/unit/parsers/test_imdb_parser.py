import os
from unittest import TestCase
from unittest.mock import patch

from RatS.data.movie import Movie
from RatS.parsers.imdb_parser import IMDBRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class IMDBParserTest(TestCase):

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        IMDBRatingsParser()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.parsers.imdb_parser.IMDBRatingsParser.parse_ratings_from_csv')
    @patch('RatS.parsers.imdb_parser.IMDBRatingsParser._rename_csv_file')
    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.imdb_parser.IMDB')
    def test_parser(self, site_mock, base_init_mock, browser_mock, rename_csv_mock, parse_csv_mock):
        parser = IMDBRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(1, rename_csv_mock.call_count)
        self.assertEqual(1, parse_csv_mock.call_count)

    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.imdb_parser.IMDB')
    def test_csv_to_json(self, site_mock, base_init_mock, browser_mock):
        parser = IMDBRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.browser = browser_mock

        parsed_movies = parser.parse_ratings_from_csv(os.path.join(TESTDATA_PATH, 'my_ratings', 'imdb.csv'))

        self.assertEqual(2, len(parsed_movies))
        self.assertEqual(Movie, type(parsed_movies[0]))
        self.assertEqual('Arrival', parsed_movies[0].title)
        self.assertEqual('tt2543164', parsed_movies[0].imdb.id)
        self.assertEqual('http://www.imdb.com/title/tt2543164/', parsed_movies[0].imdb.url)
        self.assertEqual('8', parsed_movies[0].imdb.my_rating)
