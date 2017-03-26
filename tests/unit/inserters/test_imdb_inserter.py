from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.imdb_inserter import IMDBInserter


class IMDBInserterTest(TestCase):
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
        self.movie['trakt']['overall_rating'] = '89%'
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'

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
        inserter.failed_movies = []
        inserter.site_name = 'imdb'

        inserter.insert([self.movie], 'trakt')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)
