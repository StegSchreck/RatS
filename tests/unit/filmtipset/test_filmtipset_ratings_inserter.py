import os
from unittest import TestCase
from unittest.mock import patch

from RatS.filmtipset.filmtipset_ratings_inserter import FilmtipsetRatingsInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class FilmtipsetRatingsInserterTest(TestCase):
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
        with open(os.path.join(TESTDATA_PATH, 'filmtipset', 'search_result.html'), encoding='UTF-8') as search_results:
            self.search_results = search_results.read()
        with open(os.path.join(TESTDATA_PATH, 'filmtipset', 'search_result_tile.html'),
                  encoding='UTF-8') as result_tile:
            self.search_result_tile_list = [result_tile.read()]
        with open(os.path.join(TESTDATA_PATH, 'filmtipset', 'movie_details_page.html'),
                  encoding='UTF-8') as movie_details_page:
            self.movie_details_page = movie_details_page.read()

    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        FilmtipsetRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar')
    @patch('RatS.filmtipset.filmtipset_ratings_inserter.FilmtipsetRatingsInserter._is_requested_movie')
    @patch('RatS.filmtipset.filmtipset_ratings_inserter.FilmtipsetRatingsInserter._get_search_results')
    @patch('RatS.filmtipset.filmtipset_ratings_inserter.Filmtipset')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, overview_page_mock,  # pylint: disable=too-many-arguments
                    eq_check_mock, progress_print_mock):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = FilmtipsetRatingsInserter(None)
        inserter.args = False
        inserter.site = site_mock
        inserter.site.site_name = 'Filmtipset'
        inserter.failed_movies = []

        inserter.insert([self.movie], 'IMDB')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch('RatS.filmtipset.filmtipset_ratings_inserter.Filmtipset')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_find_movie_success_by_imdb(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.movie_details_page
        inserter = FilmtipsetRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Filmtipset'
        inserter.failed_movies = []

        result = inserter._check_movie_details(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.filmtipset.filmtipset_ratings_inserter.Filmtipset')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_find_movie_success_by_year(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FilmtipsetRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Filmtipset'
        inserter.failed_movies = []

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.filmtipset.filmtipset_ratings_inserter.FilmtipsetRatingsInserter._is_requested_movie')
    @patch('RatS.filmtipset.filmtipset_ratings_inserter.FilmtipsetRatingsInserter._get_search_results')
    @patch('RatS.filmtipset.filmtipset_ratings_inserter.Filmtipset')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_find_movie_fail(self, browser_mock, base_init_mock, site_mock, tiles_mock, equality_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FilmtipsetRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Filmtipset'
        inserter.failed_movies = []
        tiles_mock.return_value = self.search_result_tile_list
        equality_mock.return_value = False

        movie2 = dict()
        movie2['title'] = 'The Matrix'
        movie2['year'] = 1995
        movie2['imdb'] = dict()
        movie2['imdb']['id'] = 'tt0137523'
        movie2['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        movie2['imdb']['my_rating'] = 9

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)
