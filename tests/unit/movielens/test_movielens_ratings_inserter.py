import os
from unittest import TestCase
from unittest.mock import patch

from RatS.movielens.movielens_ratings_inserter import MovielensRatingsInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MovielensUploaderTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'https://www.imdb.com/title/tt0137523'
        self.movie['imdb']['my_rating'] = 9

    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        MovielensRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_uploader.save_movies_to_csv')
    @patch('RatS.movielens.movielens_ratings_inserter.Movielens')
    @patch('RatS.base.base_ratings_inserter.RatingsInserter.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, impex_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        inserter = MovielensRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = 'Movielens'
        inserter.failed_movies = []
        inserter.exports_folder = TESTDATA_PATH
        inserter.csv_filename = 'converted.csv'

        inserter.insert([self.movie], 'IMDB')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(impex_mock.called)
