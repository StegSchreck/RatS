import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.data.movie import Movie
from RatS.inserters.movielense_inserter import MovielenseInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MovielenseInserterTest(TestCase):
    def setUp(self):
        self.movie = Movie()
        self.movie.title = 'Fight Club'
        self.movie.imdb.id = 'tt0137523'
        self.movie.imdb.url = 'http://www.imdb.com/title/tt0137523'
        self.movie.trakt.id = '432'
        self.movie.trakt.url = 'https://trakt.tv/movies/fight-club-1999'
        self.movie.trakt.my_rating = '10'
        self.movie.trakt.overall_rating = '89%'
        self.movie.tmdb.id = '550'
        self.movie.tmdb.url = 'https://www.themoviedb.org/movie/550'
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'movielense.json'), encoding='utf8') as search_result:
            self.search_result_json = json.loads(search_result.read())['data']['searchResults']

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        MovielenseInserter()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.inserters.movielense_inserter.print_progress')
    @patch('RatS.inserters.movielense_inserter.MovielenseInserter._get_json_from_html')
    @patch('RatS.inserters.movielense_inserter.Movielense')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, json_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        json_mock.return_value = self.search_result_json
        site_mock.browser = browser_mock
        inserter = MovielenseInserter()
        inserter.site = site_mock

        inserter.insert([self.movie])

        self.assertTrue(base_init_mock.called)
        self.assertTrue(json_mock.called)
        self.assertTrue(progress_print_mock.called)
