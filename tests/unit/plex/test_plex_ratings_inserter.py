import os
from unittest import TestCase
from unittest.mock import patch

from RatS.plex.plex_ratings_inserter import PlexRatingsInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class PlexRatingsInserterTest(TestCase):
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
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'
        with open(os.path.join(TESTDATA_PATH, 'plex', 'search_result.xml'), encoding='UTF-8') as search_results:
            self.search_results = search_results.read()
        with open(os.path.join(TESTDATA_PATH, 'plex', 'search_result_tile.xml'), encoding='UTF-8') as result_tile:
            self.search_result_tile_list = [result_tile.read()]

    @patch('RatS.plex.plex_ratings_inserter.Plex._determine_server_id')
    @patch('RatS.plex.plex_ratings_inserter.Plex._determine_movies_section_id')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock, section_id_mock, server_id_mock):
        PlexRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_inserter.RatingsInserter.print_progress')
    @patch('RatS.plex.plex_ratings_inserter.PlexRatingsInserter._is_requested_movie')
    @patch('RatS.plex.plex_ratings_inserter.PlexRatingsInserter._get_search_results')
    @patch('RatS.plex.plex_ratings_inserter.Plex')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, overview_page_mock,  # pylint: disable=too-many-arguments
                    eq_check_mock, progress_print_mock):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = PlexRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Plex'
        inserter.failed_movies = []

        inserter.insert([self.movie], 'IMDB')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch('RatS.plex.plex_ratings_inserter.PlexRatingsInserter._wait_for_movie_page_to_be_loaded')
    @patch('RatS.plex.plex_ratings_inserter.Plex')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_find_movie_success(self, browser_mock, base_init_mock, site_mock, page_load_wait_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = PlexRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Plex'
        inserter.failed_movies = []

        result = inserter._find_movie(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.plex.plex_ratings_inserter.PlexRatingsInserter._is_requested_movie')
    @patch('RatS.plex.plex_ratings_inserter.PlexRatingsInserter._get_search_results')
    @patch('RatS.plex.plex_ratings_inserter.Plex')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.base.base_site.Firefox')
    def test_find_movie_fail(self, browser_mock, base_init_mock, site_mock, tiles_mock, equality_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = PlexRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Plex'
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
