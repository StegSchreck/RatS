from unittest import TestCase
from unittest.mock import patch

from RatS.base.base_ratings_parser import RatingsParser


class BaseParserTest(TestCase):
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock):
        with patch("RatS.base.base_site.BaseSite") as site_mock:
            parser = RatingsParser(site_mock, None)

            self.assertEqual(parser.site, site_mock)
