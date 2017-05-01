import os
from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.letterboxd_uploader import LetterboxdUploader

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class LetterboxdUploaderTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['imdb']['my_rating'] = 9

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        LetterboxdUploader()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.inserters.letterboxd_uploader.LetterboxdUploader._wait_for_import_processing')
    @patch('RatS.inserters.letterboxd_uploader.LetterboxdUploader._wait_for_movie_matching')
    @patch('RatS.inserters.letterboxd_uploader.save_movies_to_csv')
    @patch('RatS.inserters.letterboxd_uploader.Letterboxd')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, impex_mock, matching_mock, process_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        inserter = LetterboxdUploader()
        inserter.site = site_mock
        inserter.site.site_name = 'Letterboxd'
        inserter.failed_movies = []
        inserter.exports_folder = TESTDATA_PATH

        inserter.insert([self.movie], 'IMDB')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(impex_mock.called)
