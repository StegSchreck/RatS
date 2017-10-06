import os
from unittest import TestCase
from unittest.mock import patch

from RatS.trakt.trakt_ratings_parser import TraktRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class TraktRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'trakt', 'my_ratings.html'), encoding='UTF-8') as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(os.path.join(TESTDATA_PATH, 'trakt', 'movie_details_page.html'), encoding='UTF-8') as detail_page:
            self.detail_page = detail_page.read()
        with open(os.path.join(TESTDATA_PATH, 'trakt', 'movie_details_page_missing_imdb_id.html'),
                  encoding='UTF-8') as detail_page_without_imdb_id:
            self.detail_page_without_imdb_id = detail_page_without_imdb_id.read()

    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        TraktRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_parser.RatingsParser._print_progress_bar')
    @patch('RatS.trakt.trakt_ratings_parser.TraktRatingsParser.parse_movie_details_page')
    @patch('RatS.base.base_site.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.trakt.trakt_ratings_parser.Trakt')
    def test_parser(self, site_mock, base_init_mock, browser_mock, parse_movie_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Trakt'
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(60, parse_movie_mock.call_count)
        self.assertEqual(60, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Arrival', parser.movies[0]['title'])
        self.assertEqual('210803', parser.movies[0]['trakt']['id'])
        self.assertEqual('https://trakt.tv/movies/arrival-2016', parser.movies[0]['trakt']['url'])

    @patch('RatS.base.base_site.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.trakt.trakt_ratings_parser.Trakt')
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser(None)
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

    @patch('RatS.base.base_site.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.trakt.trakt_ratings_parser.Trakt')
    def test_parser_single_movie_with_missing_imdb_id(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Trakt'
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page_without_imdb_id
        movie = dict()

        parser.parse_movie_details_page(movie)

        # Top Gear Patagonia
        self.assertEqual(2014, movie['year'])
        self.assertNotIn('imdb', movie)
        self.assertEqual('314390', movie['tmdb']['id'])
        self.assertEqual('https://www.themoviedb.org/movie/314390', movie['tmdb']['url'])
        self.assertEqual(8, movie['trakt']['my_rating'])
