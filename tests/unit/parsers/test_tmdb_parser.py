import os
from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.tmdb_parser import TMDBRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class TMDBParserTest(TestCase):

    def setUp(self):
        with open(os.path.join(TESTDATA_PATH, 'my_ratings', 'tmdb.html'), encoding='utf8') as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(os.path.join(TESTDATA_PATH, 'movie_details_page', 'tmdb.html'), encoding='utf8') as detail_page:
            self.detail_page = detail_page.read()

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        TMDBRatingsParser()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.parsers.base_parser.print_progress')
    @patch('RatS.parsers.tmdb_parser.TMDBRatingsParser.parse_movie_details_page')
    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.tmdb_parser.TMDB')
    def test_parser(self, site_mock, base_init_mock, browser_mock, parse_movie_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = TMDBRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'tmdb'
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(20, parse_movie_mock.call_count)
        self.assertEqual(20, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Logan', parser.movies[0]['title'])
        self.assertEqual('263115', parser.movies[0]['tmdb']['id'])
        self.assertEqual('https://www.themoviedb.org/movie/263115', parser.movies[0]['tmdb']['url'])

    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.tmdb_parser.TMDB')
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = TMDBRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'tmdb'
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = dict()

        parser.parse_movie_details_page(movie)

        self.assertEqual(8, movie['tmdb']['my_rating'])
        self.assertEqual(2017, movie['year'])
