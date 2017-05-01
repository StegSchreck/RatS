import os
from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.trakt_parser import TraktRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class TraktParserTest(TestCase):

    def setUp(self):
        with open(os.path.join(TESTDATA_PATH, 'my_ratings', 'trakt.html'), encoding='utf8') as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(os.path.join(TESTDATA_PATH, 'movie_details_page', 'trakt.html'), encoding='utf8') as detail_page:
            self.detail_page = detail_page.read()

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        TraktRatingsParser()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.parsers.base_parser.print_progress')
    @patch('RatS.parsers.trakt_parser.TraktRatingsParser.parse_movie_details_page')
    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.trakt_parser.Trakt')
    def test_parser(self, site_mock, base_init_mock, browser_mock, parse_movie_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Trakt'
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(60, parse_movie_mock.call_count)
        self.assertEqual(60, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Arrival', parser.movies[0]['title'])
        self.assertEqual('210803', parser.movies[0]['trakt']['id'])
        self.assertEqual('https://trakt.tv/movies/arrival-2016', parser.movies[0]['trakt']['url'])

    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.trakt_parser.Trakt')
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Trakt'
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = dict()

        parser.parse_movie_details_page(movie)

        # Fight Club
        self.assertEqual(1999, movie['year'])
        self.assertEqual('tt0137523', movie['imdb']['id'])
        self.assertEqual('http://www.imdb.com/title/tt0137523', movie['imdb']['url'])
        self.assertEqual('550', movie['tmdb']['id'])
        self.assertEqual('https://www.themoviedb.org/movie/550', movie['tmdb']['url'])
        self.assertEqual(10, movie['trakt']['my_rating'])
