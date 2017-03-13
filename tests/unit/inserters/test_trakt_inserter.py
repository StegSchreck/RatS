import os
from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.trakt_inserter import TraktInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class TraktInserterTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['imdb']['my_rating'] = 9
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'trakt.html'), encoding='utf8') as search_result_tile:
            self.search_result = [search_result_tile.read()]

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        TraktInserter()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.inserters.trakt_inserter.print_progress')
    @patch('RatS.inserters.trakt_inserter.TraktInserter._is_requested_movie')
    @patch('RatS.inserters.trakt_inserter.TraktInserter._get_movie_tiles')
    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, overview_page_mock, eq_check_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        overview_page_mock.return_value = self.search_result
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = TraktInserter()
        inserter.site = site_mock

        inserter.insert([self.movie], 'imdb')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)
