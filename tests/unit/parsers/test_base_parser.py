from unittest import TestCase
from unittest.mock import patch

from RatS.parsers.base_parser import Parser


class BaseParserTest(TestCase):

    @patch('RatS.parsers.base_parser.PhantomJS')
    def test_init(self, browser_mock):
        with patch('RatS.sites.base_site.Site') as site_mock:
            parser = Parser(site_mock)

            self.assertEqual(parser.site, site_mock)
            self.assertTrue(browser_mock.called)
            self.assertTrue(site_mock.login.called)
