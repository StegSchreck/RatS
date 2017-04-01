import os
from unittest import TestCase
from unittest.mock import patch

from bs4 import BeautifulSoup

from RatS.inserters.imdb_inserter import IMDBInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class IMDBInserterTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['year'] = 1999
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['trakt'] = dict()
        self.movie['trakt']['id'] = '432'
        self.movie['trakt']['url'] = 'https://trakt.tv/movies/fight-club-1999'
        self.movie['trakt']['my_rating'] = '10'
        self.movie['trakt']['overall_rating'] = '89%'
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'imdb.html'), encoding='utf8') as search_result_tile:
            self.search_result = search_result_tile.read()

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        IMDBInserter()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.inserters.imdb_inserter.print_progress')
    @patch('RatS.inserters.imdb_inserter.IMDB')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        inserter = IMDBInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'imdb'
        inserter.failed_movies = []

        inserter.insert([self.movie], 'trakt')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch('RatS.inserters.imdb_inserter.IMDB')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_is_requested_movie_success(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = IMDBInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'imdb'
        inserter.failed_movies = []
        search_result_page = BeautifulSoup(self.search_result, 'html.parser')
        search_result = search_result_page.find(class_='findList').find_all(class_='findResult')[0]

        result = inserter._is_requested_movie(self.movie, search_result)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.imdb_inserter.IMDB')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_is_requested_movie_fail(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = IMDBInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'imdb'
        inserter.failed_movies = []
        search_result_page = BeautifulSoup(self.search_result, 'html.parser')
        search_result = search_result_page.find(class_='findList').find_all(class_='findResult')[0]

        movie2 = dict()
        movie2['title'] = 'Arrival'
        movie2['year'] = 2006

        result = inserter._is_requested_movie(movie2, search_result)  # pylint: disable=protected-access

        self.assertFalse(result)
