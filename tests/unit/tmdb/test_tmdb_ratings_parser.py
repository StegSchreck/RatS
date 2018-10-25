import os
from unittest import TestCase
from unittest.mock import patch

from RatS.tmdb.tmdb_ratings_parser import TMDBRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class TMDBParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'tmdb', 'my_ratings.html'), encoding='UTF-8') as my_ratings:
            self.my_ratings = my_ratings.read()

    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        TMDBRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_parser.RatingsParser._print_progress_bar')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.tmdb.tmdb_ratings_parser.TMDB')
    def test_parser(self, site_mock, base_init_mock, browser_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = TMDBRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'TMDB'
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(50, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Ghost in the Shell: The New Movie', parser.movies[0]['title'])
        self.assertEqual(2017, parser.movies[0]['year'])
        self.assertEqual('334376', parser.movies[0]['tmdb']['id'])
        self.assertEqual('https://www.themoviedb.org/movie/334376', parser.movies[0]['tmdb']['url'])
        self.assertEqual(6, parser.movies[0]['tmdb']['my_rating'])
