import os
from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.listal_parser import ListalRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class ListalParserTest(TestCase):

    def setUp(self):
        with open(os.path.join(TESTDATA_PATH, 'my_ratings', 'listal.html'), encoding='UTF-8') as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(os.path.join(TESTDATA_PATH, 'movie_details_page', 'listal.html'), encoding='UTF-8') as detail_page:
            self.detail_page = detail_page.read()

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        ListalRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.parsers.base_parser.Parser.print_progress')
    @patch('RatS.parsers.listal_parser.ListalRatingsParser.parse_movie_details_page')
    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.listal_parser.Listal')
    def test_parser(self, site_mock, base_init_mock, browser_mock, parse_movie_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = ListalRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Listal'
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(60, parse_movie_mock.call_count)
        self.assertEqual(60, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Fight Club', parser.movies[0]['title'])
        self.assertEqual('1596', parser.movies[0]['listal']['id'])
        self.assertEqual('http://www.listal.com/movie/fight-club', parser.movies[0]['listal']['url'])

    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.listal_parser.Listal')
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = ListalRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Listal'
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = dict()

        parser.parse_movie_details_page(movie)

        self.assertEqual(1999, movie['year'])
        self.assertEqual(10, movie['listal']['my_rating'])
        self.assertEqual('tt0137523', movie['imdb']['id'])
        self.assertEqual('http://www.imdb.com/title/tt0137523', movie['imdb']['url'])
