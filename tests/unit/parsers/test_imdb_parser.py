import os
from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.imdb_parser import IMDBRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class IMDBParserTest(TestCase):

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        IMDBRatingsParser()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.utils.file_impex.load_movies_from_csv')
    @patch('RatS.parsers.imdb_parser.IMDBRatingsParser._rename_csv_file')
    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.imdb_parser.IMDB')
    def test_parser(self, site_mock, base_init_mock, browser_mock, rename_csv_mock, parse_csv_mock):  # pylint: disable=too-many-arguments
        parser = IMDBRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'imdb'
        parser.site.browser = browser_mock
        parser.exports_folder = os.path.abspath(os.path.join(TESTDATA_PATH, 'exports'))
        parser.csv_filename = '1234567890_imdb.csv'

        parser.parse()

        self.assertEqual(1, rename_csv_mock.call_count)
        self.assertEqual(1, parse_csv_mock.call_count)

    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.imdb_parser.IMDB')
    def test_csv_rename(self, site_mock, base_init_mock, browser_mock):  # pylint: disable=too-many-arguments
        parser = IMDBRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'imdb'
        parser.site.browser = browser_mock
        parser.exports_folder = os.path.abspath(os.path.join(TESTDATA_PATH, 'exports'))
        parser.csv_filename = '1234567890_imdb.csv'

        self.assertFalse(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', 'ratings.csv')))
        with open(os.path.join(TESTDATA_PATH, 'exports', 'ratings.csv'), 'w+'):
            self.assertTrue(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', 'ratings.csv')))
        self.assertFalse(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', parser.csv_filename)))

        parser._rename_csv_file()  # pylint: disable=protected-access

        self.assertFalse(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', 'ratings.csv')))
        self.assertTrue(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', parser.csv_filename)))
        os.remove(os.path.join(TESTDATA_PATH, 'exports', parser.csv_filename))
