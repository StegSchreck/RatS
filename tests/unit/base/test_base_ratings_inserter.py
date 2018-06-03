from unittest import TestCase
from unittest.mock import patch

from RatS.base.base_ratings_inserter import RatingsInserter


class BaseInserterTest(TestCase):

    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock):
        with patch('RatS.base.base_site.Site') as site_mock:
            inserter = RatingsInserter(site_mock, None)

            self.assertEqual(inserter.site, site_mock)
