import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.flixster_parser import FlixsterRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class FlixsterParserTest(TestCase):

    def setUp(self):
        with open(os.path.join(TESTDATA_PATH, 'my_ratings', 'flixster.json'), encoding='UTF-8') as my_ratings:
            self.my_ratings = json.loads(my_ratings.read())

    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        FlixsterRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.parsers.base_parser.Parser.print_progress')
    @patch('RatS.parsers.flixster_parser.Flixster.get_json_from_html')
    @patch('RatS.sites.base_site.Firefox')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.flixster_parser.Flixster')
    def test_parser(self, site_mock, base_init_mock, browser_mock, json_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        json_mock.return_value = self.my_ratings
        parser = FlixsterRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Flixster'
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(330 - 9, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Fight Club', parser.movies[0]['title'])
        self.assertEqual(1999, parser.movies[0]['year'])

        self.assertEqual(13153, parser.movies[0]['flixster']['id'])
        self.assertEqual('http://www.flixster.com/movie/fight-club/', parser.movies[0]['flixster']['url'])
        self.assertEqual(10, parser.movies[0]['flixster']['my_rating'])
