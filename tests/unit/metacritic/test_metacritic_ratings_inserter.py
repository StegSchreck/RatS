import os
from unittest import TestCase
from unittest.mock import patch

from bs4 import BeautifulSoup

from RatS.metacritic.metacritic_ratings_inserter import MetacriticRatingsInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MetacriticRatingsInserterTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['year'] = 1999
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['imdb']['my_rating'] = 9
        with open(os.path.join(TESTDATA_PATH, 'metacritic', 'search_result.html'), encoding='UTF-8') as search_results:
            self.search_results = search_results.read()
        with open(os.path.join(TESTDATA_PATH, 'metacritic', 'search_result_tile.html'),
                  encoding='UTF-8') as result_tile:
            self.search_result_tile_list = [result_tile.read()]
        with open(os.path.join(TESTDATA_PATH, 'metacritic', 'movie_details_page.html'),
                  encoding='UTF-8') as movie_details_page:
            self.movie_details_page = movie_details_page.read()

    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        MetacriticRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar')
    @patch('RatS.metacritic.metacritic_ratings_inserter.MetacriticRatingsInserter._is_requested_movie')
    @patch('RatS.metacritic.metacritic_ratings_inserter.MetacriticRatingsInserter._get_search_results')
    @patch('RatS.metacritic.metacritic_ratings_inserter.Metacritic')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, overview_page_mock,  # pylint: disable=too-many-arguments
                    eq_check_mock, progress_print_mock):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = MetacriticRatingsInserter(None)
        inserter.args = False
        inserter.site = site_mock
        inserter.site.site_name = 'Metacritic'
        inserter.failed_movies = []

        inserter.insert([self.movie], 'IMDB')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch('RatS.metacritic.metacritic_ratings_inserter.MetacriticRatingsInserter._is_requested_movie')
    @patch('RatS.metacritic.metacritic_ratings_inserter.MetacriticRatingsInserter._get_search_results')
    @patch('RatS.metacritic.metacritic_ratings_inserter.Metacritic')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_find_movie_success(self, browser_mock, base_init_mock, site_mock, tiles_mock, equality_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = MetacriticRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Metacritic'
        inserter.failed_movies = []
        tiles_mock.return_value = self.search_result_tile_list
        equality_mock.return_value = True

        result = inserter._find_movie(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.metacritic.metacritic_ratings_inserter.MetacriticRatingsInserter._is_requested_movie')
    @patch('RatS.metacritic.metacritic_ratings_inserter.MetacriticRatingsInserter._get_search_results')
    @patch('RatS.metacritic.metacritic_ratings_inserter.Metacritic')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_find_movie_fail(self, browser_mock, base_init_mock, site_mock, tiles_mock, equality_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = MetacriticRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Metacritic'
        inserter.failed_movies = []
        tiles_mock.return_value = self.search_result_tile_list
        equality_mock.return_value = False

        movie2 = dict()
        movie2['title'] = 'The Matrix'
        movie2['year'] = 1995

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch('RatS.metacritic.metacritic_ratings_inserter.Metacritic')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_compare_movie_success(self, browser_mock, base_init_mock, site_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.movie_details_page
        inserter = MetacriticRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Metacritic'
        inserter.failed_movies = []

        search_result = BeautifulSoup(self.search_result_tile_list[0], 'html.parser')
        result = inserter._is_requested_movie(self.movie, search_result)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.metacritic.metacritic_ratings_inserter.Metacritic')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_compare_movie_fail(self, browser_mock, base_init_mock, site_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.movie_details_page
        inserter = MetacriticRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Metacritic'
        inserter.failed_movies = []

        movie2 = dict()
        movie2['title'] = 'The Matrix'
        movie2['year'] = 1995

        search_result = BeautifulSoup(self.search_result_tile_list[0], 'html.parser')
        result = inserter._is_requested_movie(movie2, search_result)  # pylint: disable=protected-access

        self.assertFalse(result)
