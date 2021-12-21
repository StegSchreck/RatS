import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.base_site import BaseSite
from RatS.base.movie_entity import Site
from RatS.plex.plex_site import Plex

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class PlexSiteTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))

    @patch("RatS.plex.plex_site.Plex._parse_configuration")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_site.BaseSite._init_browser")
    def test_determine_server_id(
        self, init_browser_mock, browser_mock, configuration_mock
    ):
        browser_mock.current_url = (
            "http://localhost/web/index.html#!/settings/server/ThisIsAMockUUID/general"
        )
        site = Plex(None)
        site.browser = browser_mock
        site.BASE_URL = "localhost"

        result = site._determine_server_id()  # pylint: disable=protected-access

        self.assertEqual("ThisIsAMockUUID", result)

    @patch("RatS.base.base_site.BaseSite._insert_login_credentials")
    @patch("RatS.plex.plex_site.Plex._parse_configuration")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_site.BaseSite._init_browser")
    def test_insert_login_credentials(
        self, init_browser_mock, browser_mock, configuration_mock, base_site_mock
    ):
        browser_mock.current_url = (
            "http://localhost/web/index.html#!/settings/server/ThisIsAMockUUID/general"
        )
        site: BaseSite = Plex(None)
        site.site = Site.PLEX
        site.browser = browser_mock
        site.BASE_URL = "localhost"

        site._insert_login_credentials()  # pylint: disable=protected-access

        self.assertTrue(base_site_mock.called)

    @patch("RatS.plex.plex_site.Plex._determine_plex_token")
    @patch("RatS.plex.plex_site.Plex._determine_server_id")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_site.BaseSite._init_browser")
    def test_parse_configuration(
        self, init_browser_mock, browser_mock, server_id_mock, plex_token_mock
    ):
        browser_mock.current_url = (
            "http://localhost/web/index.html#!/settings/server/ThisIsAMockUUID/general"
        )
        site = Plex(None)
        site.browser = browser_mock
        server_id_mock.return_value = "ThisIsAMockUUID"
        plex_token_mock.return_value = "ThisIsAMockToken"
        site.BASE_URL = "localhost"

        site._parse_configuration()  # pylint: disable=protected-access

        self.assertTrue(server_id_mock.called)
        self.assertTrue(plex_token_mock.called)
        self.assertEqual(
            "http://localhost/library/all?type=1&userRating!=0"
            "&X-Plex-Container-Start=0&X-Plex-Container-Size=100"
            "&X-Plex-Token=ThisIsAMockToken",
            site.MY_RATINGS_URL,
        )

    @patch("re.findall")
    @patch("RatS.plex.plex_site.Plex._parse_configuration")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_site.BaseSite._init_browser")
    def test_determine_plex_token(
        self, init_browser_mock, browser_mock, configuration_mock, regex_mock
    ):
        browser_mock.current_url = (
            "http://localhost/web/index.html#!/settings/server/ThisIsAMockUUID/general"
        )
        site = Plex(None)
        site.browser = browser_mock
        site.SERVER_ID = "ThisIsAMockUUID"
        site.BASE_URL = "localhost"
        regex_mock.return_value = ["ThisIsAMockToken"]

        result = site._determine_plex_token()  # pylint: disable=protected-access

        self.assertEqual("ThisIsAMockToken", result)
