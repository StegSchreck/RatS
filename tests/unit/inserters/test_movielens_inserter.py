import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.movielens_inserter import MovielensInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MovielensInserterTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['trakt'] = dict()
        self.movie['trakt']['id'] = '432'
        self.movie['trakt']['url'] = 'https://trakt.tv/movies/fight-club-1999'
        self.movie['trakt']['my_rating'] = '10'
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'movielens.json'), encoding='utf8') as search_result:
            self.search_result_json = json.loads(search_result.read())['data']

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        MovielensInserter()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.inserters.movielens_inserter.print_progress')
    @patch('RatS.inserters.movielens_inserter.Movielens.get_json_from_html')
    @patch('RatS.inserters.movielens_inserter.Movielens')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, json_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        json_mock.return_value = self.search_result_json
        site_mock.browser = browser_mock
        inserter = MovielensInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Movielens'
        inserter.failed_movies = []

        inserter.insert([self.movie], 'Trakt')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(json_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch('RatS.inserters.movielens_inserter.Movielens')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_is_requested_movie_success_imdb(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = MovielensInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Movielens'
        inserter.failed_movies = []
        movie_to_test = self.search_result_json['searchResults'][0]['movie']

        result = inserter._is_requested_movie(self.movie, movie_to_test)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.movielens_inserter.Movielens')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_is_requested_movie_success_tmdb(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = MovielensInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Movielens'
        inserter.failed_movies = []
        movie_to_test = self.search_result_json['searchResults'][0]['movie']

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999
        movie2['tmdb'] = dict()
        movie2['tmdb']['id'] = '550'
        movie2['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'

        result = inserter._is_requested_movie(movie2, movie_to_test)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.movielens_inserter.Movielens')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_is_requested_movie_success_movielens(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = MovielensInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Movielens'
        inserter.failed_movies = []
        movie_to_test = self.search_result_json['searchResults'][0]['movie']

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999
        movie2['movielens'] = dict()
        movie2['movielens']['id'] = '2959'
        movie2['movielens']['url'] = 'https://movielens.org/movies/2959'
        movie2['movielens']['my_rating'] = '10'

        result = inserter._is_requested_movie(movie2, movie_to_test)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.movielens_inserter.Movielens')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_is_requested_movie_success_year(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = MovielensInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Movielens'
        inserter.failed_movies = []
        movie_to_test = self.search_result_json['searchResults'][0]['movie']

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999

        result = inserter._is_requested_movie(movie2, movie_to_test)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.movielens_inserter.Movielens')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_is_requested_movie_fail(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = MovielensInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'Movielens'
        inserter.failed_movies = []
        movie_to_test = self.search_result_json['searchResults'][0]['movie']

        movie2 = dict()
        movie2['title'] = 'Arrival'
        movie2['year'] = 2006

        result = inserter._is_requested_movie(movie2, movie_to_test)  # pylint: disable=protected-access

        self.assertFalse(result)
