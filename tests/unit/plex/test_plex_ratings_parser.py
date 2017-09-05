import os
from unittest import TestCase
from unittest.mock import patch

from bs4 import BeautifulSoup

from RatS.plex.plex_ratings_parser import PlexRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class PlexRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'plex', 'my_ratings.xml'), encoding='UTF-8') as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(os.path.join(TESTDATA_PATH, 'plex', 'my_ratings_tile.xml'), encoding='UTF-8') as ratings_tile:
            self.ratings_tile = BeautifulSoup(ratings_tile.read(), 'html.parser').find('video', attrs={'type': 'movie'})

    @patch('RatS.plex.plex_ratings_inserter.Plex._determine_server_id')
    @patch('RatS.plex.plex_ratings_inserter.Plex._determine_movies_section_id')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock, section_id_mock, server_id_mock):
        PlexRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.plex.plex_ratings_parser.PlexRatingsParser._print_progress_bar')
    @patch('RatS.plex.plex_ratings_parser.PlexRatingsParser._parse_movie_tile')
    @patch('RatS.base.base_site.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.plex.plex_ratings_parser.Plex')
    def test_parser(self, site_mock, base_init_mock, browser_mock, parse_movie_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = PlexRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Plex'
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(20, parse_movie_mock.call_count)
        self.assertEqual(20, len(parser.movies))

    @patch('RatS.base.base_site.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.plex.plex_ratings_parser.Plex')
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = PlexRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Plex'
        parser.site.BASE_URL = 'localhost:12345'
        parser.site.SERVER_ID = 'ThisIsAMockUUID'
        parser.site.browser = browser_mock

        movie = parser._parse_movie_tile(self.ratings_tile)  # pylint: disable=protected-access

        self.assertEqual(dict, type(movie))
        self.assertEqual('Fight Club', movie['title'])
        self.assertEqual(1999, movie['year'])
        self.assertEqual(10, movie['plex']['my_rating'])
        self.assertEqual('19542', movie['plex']['id'])
        self.assertEqual('http://localhost:12345/web/index.html#!'
                         '/server/ThisIsAMockUUID/'
                         'details/%2Flibrary%2Fmetadata%2F19542', movie['plex']['url'])
