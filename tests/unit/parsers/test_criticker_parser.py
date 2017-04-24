import os
from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.criticker_parser import CritickerRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class CritickerParserTest(TestCase):

    def setUp(self):
        with open(os.path.join(TESTDATA_PATH, 'my_ratings', 'criticker.xml'), encoding='utf8') as my_ratings:
            self.my_ratings = my_ratings.read()

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        CritickerRatingsParser()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.criticker_parser.Criticker')
    def test_parser(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = CritickerRatingsParser()
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'criticker'
        parser.site.browser = browser_mock
        parser.exports_folder = os.path.abspath(os.path.join(TESTDATA_PATH, 'exports'))

        parser.parse()

        self.assertEqual(1019, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Fight Club', parser.movies[0]['title'])
        self.assertEqual(1999, parser.movies[0]['year'])
        self.assertEqual('1077', parser.movies[0]['criticker']['id'])
        self.assertEqual('https://www.criticker.com/film/Fight-Club', parser.movies[0]['criticker']['url'])
        self.assertEqual(10, parser.movies[0]['criticker']['my_rating'])
        self.assertEqual('tt0137523', parser.movies[0]['imdb']['id'])
        self.assertEqual('http://www.imdb.com/title/tt0137523', parser.movies[0]['imdb']['url'])

        os.remove(os.path.join(TESTDATA_PATH, 'exports', parser.xml_filename))
