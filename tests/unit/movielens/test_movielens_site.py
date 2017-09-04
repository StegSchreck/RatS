import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.movielens.movielens_site import Movielens

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MovielensSiteTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'movielens', 'my_ratings.json'), encoding='UTF-8') as my_ratings:
            self.my_ratings_pre = my_ratings.read()
            self.my_ratings_json = json.loads(self.my_ratings_pre)

    @patch('RatS.base.base_site.Firefox')
    @patch('RatS.base.base_site.Site._init_browser')
    def test_get_json_from_html(self, init_browser_mock, browser_mock):
        site = Movielens(None)
        site.browser = browser_mock
        browser_mock.find_element_by_tag_name.return_value.text = self.my_ratings_pre

        result = site.get_json_from_html()

        self.assertEqual(self.my_ratings_json, result)
