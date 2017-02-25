from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.movielense_inserter import MovielenseInserter
from RatS.sites.movielense_site import Movielense


class MovielenseInserterTest(TestCase):

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.PhantomJS')
    def test_init(self, browser_mock, base_init_mock):
        MovielenseInserter()

        self.assertTrue(base_init_mock.called)
