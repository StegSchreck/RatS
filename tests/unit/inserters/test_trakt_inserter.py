import os
from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.trakt_inserter import TraktRatingsInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class TraktRatingsInserterTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['year'] = 1999
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['imdb']['my_rating'] = 9
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'trakt.html'), encoding='UTF-8') as search_results:
            self.search_results = search_results.read()
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'trakt_tile.html'), encoding='UTF-8') as result_tile:
            self.search_result_tile_list = [result_tile.read()]
        with open(os.path.join(TESTDATA_PATH, 'movie_details_page', 'trakt.html'),
                  encoding='UTF-8') as movie_details_page:
            self.movie_details_page = movie_details_page.read()

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        TraktRatingsInserter()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.inserters.base_inserter.print_progress')
    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._is_requested_movie')
    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._get_search_results')
    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, overview_page_mock,  # pylint: disable=too-many-arguments
                    eq_check_mock, progress_print_mock):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []

        inserter.insert([self.movie], 'IMDB')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_external_link_compare_imdb_success(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []

        result = inserter._compare_external_links(self.movie_details_page, self.movie, 'imdb.com', 'imdb')  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_external_link_compare_imdb_fail(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999
        movie2['imdb'] = dict()
        movie2['imdb']['id'] = 'tt0137523'
        movie2['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        movie2['imdb']['my_rating'] = 10

        result = inserter._compare_external_links(self.movie_details_page, movie2, 'imdb.com', 'imdb')  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_external_link_compare_tmdb_success(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []

        result = inserter._compare_external_links(self.movie_details_page, self.movie, 'themoviedb.org', 'tmdb')  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_external_link_compare_tmdb_fail(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []

        movie2 = dict()
        movie2['title'] = 'Arrival'
        movie2['year'] = 2006
        movie2['tmdb'] = dict()
        movie2['tmdb']['id'] = '329865'
        movie2['tmdb']['url'] = 'https://www.themoviedb.org/movie/329865'
        movie2['tmdb']['my_rating'] = 7

        result = inserter._compare_external_links(self.movie_details_page, movie2, 'themoviedb.org', 'tmdb')  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._compare_external_links')
    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_find_movie_success_by_imdb(self, browser_mock, base_init_mock, site_mock, compare_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []
        compare_mock.return_value = True

        result = inserter._find_movie(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._compare_external_links')
    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_find_movie_success_by_tmdb(self, browser_mock, base_init_mock, site_mock, compare_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []
        compare_mock.return_value = True

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999
        movie2['tmdb'] = dict()
        movie2['tmdb']['id'] = '550'
        movie2['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'
        movie2['tmdb']['my_rating'] = 9

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._compare_external_links')
    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_find_movie_success_by_year(self, browser_mock, base_init_mock, site_mock, compare_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []
        compare_mock.return_value = True

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._is_requested_movie')
    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._get_search_results')
    @patch('RatS.inserters.trakt_inserter.TraktRatingsInserter._compare_external_links')
    @patch('RatS.inserters.trakt_inserter.Trakt')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_find_movie_fail(self, browser_mock, base_init_mock, site_mock, compare_mock, tiles_mock, equality_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = TraktRatingsInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Trakt'
        inserter.failed_movies = []
        compare_mock.return_value = False
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
