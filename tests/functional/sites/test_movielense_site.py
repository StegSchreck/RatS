from unittest import TestCase

from RatS.sites.movielense_site import Movielense


class MovielenseSiteTest(TestCase):
    def setUp(self):
        self.site = Movielense()

    def test_login(self):
        self.assertEqual('https://movielens.org/home', self.site.browser.current_url)

    def tearDown(self):
        self.site.browser.quit()
