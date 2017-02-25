from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.base_inserter import Inserter


class BaseInserterTest(TestCase):

    @patch('RatS.sites.base_site.PhantomJS')
    def test_init(self, browser_mock):
        with patch('RatS.sites.base_site.Site') as site_mock:
            inserter = Inserter(site_mock)

            self.assertEqual(inserter.site, site_mock)
