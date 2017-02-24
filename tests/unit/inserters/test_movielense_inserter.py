from unittest import TestCase

from RatS.inserters.movielense_inserter import MovielenseInserter
from RatS.sites.movielense_site import Movielense


class MovielenseInserterTest(TestCase):
    def test_init(self):
        inserter = MovielenseInserter()
        self.assertTrue(Movielense, type(inserter.site))
