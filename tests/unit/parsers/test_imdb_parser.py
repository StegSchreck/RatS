from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.imdb_parser import IMDBRatingsParser


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

        parser.parse()

        self.assertEqual(1, rename_csv_mock.call_count)
        self.assertEqual(1, parse_csv_mock.call_count)
