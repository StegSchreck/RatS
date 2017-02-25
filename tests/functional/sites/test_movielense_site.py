from unittest import TestCase
from unittest import skip

from RatS.sites.movielense_site import Movielense


@skip('movielense not working from travis')
class MovielenseSiteTest(TestCase):
    def setUp(self):
        self.site = Movielense()

    def test_login(self):
        self.assertEqual('https://movielens.org/home', self.site.browser.current_url)

    def tearDown(self):
        self.site.kill_browser()
