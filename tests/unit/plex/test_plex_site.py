import os
from unittest import TestCase
from unittest.mock import patch

from RatS.plex.plex_site import Plex

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class PlexSiteTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'plex', 'sections.xml'), encoding='UTF-8') as server_sections:
            self.server_sections = server_sections.read()

    @patch('RatS.plex.plex_site.Plex._parse_configuration')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_site.Site._init_browser')
    def test_determine_movie_section_id(self, init_browser_mock, browser_mock, configuration_mock):
        browser_mock.page_source = self.server_sections
        site = Plex(None)
        site.browser = browser_mock
        site.BASE_URL = 'localhost'

        result = site._determine_movies_section_id()  # pylint: disable=protected-access

        self.assertEqual('5', result)

    @patch('RatS.plex.plex_site.Plex._parse_configuration')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_site.Site._init_browser')
    def test_determine_server_id(self, init_browser_mock, browser_mock, configuration_mock):
        browser_mock.current_url = 'http://localhost/web/index.html#!/settings/server/ThisIsAMockUUID/general'
        site = Plex(None)
        site.browser = browser_mock
        site.BASE_URL = 'localhost'

        result = site._determine_server_id()  # pylint: disable=protected-access

        self.assertEqual('ThisIsAMockUUID', result)
