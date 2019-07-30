import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.rottentomatoes.rottentomatoes_ratings_parser import RottenTomatoesRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class RottenTomatoesRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'rottentomatoes', 'my_ratings_last_page.json'), encoding='UTF-8') as my_ratings:
            self.my_ratings = json.loads(my_ratings.read())

    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        RottenTomatoesRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.rottentomatoes.rottentomatoes_ratings_parser.RottenTomatoes.get_json_from_html')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.rottentomatoes.rottentomatoes_ratings_parser.RottenTomatoes')
    def test_parser(self, site_mock, base_init_mock, browser_mock, json_mock):
        json_mock.return_value = self.my_ratings
        parser = RottenTomatoesRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'RottenTomatoes'
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(20, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Sleepless', parser.movies[0]['title'])
        self.assertEqual(2017, parser.movies[0]['year'])

        self.assertEqual('12880636', parser.movies[0]['rottentomatoes']['id'])
        self.assertEqual('https://www.rottentomatoes.com/m/sleepless', parser.movies[0]['rottentomatoes']['url'])
        self.assertEqual(6, parser.movies[0]['rottentomatoes']['my_rating'])
