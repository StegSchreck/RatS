from unittest import TestCase

from RatS.sites.movielense_site import Movielense


class MovielenseSiteTest(TestCase):
    def test_login(self):
        self.site = Movielense()
        self.assertEqual('https://movielens.org/home', self.site.browser.current_url)

    def tearDown(self):
        self.site.browser.quit()
