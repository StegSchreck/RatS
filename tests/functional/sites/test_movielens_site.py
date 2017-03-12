from unittest import TestCase
from unittest import skip

from RatS.sites.movielens_site import Movielens


@skip('movielens not working from travis')
class MovielensSiteTest(TestCase):
    def setUp(self):
        self.site = Movielens()

    def test_login(self):
        self.assertEqual('https://movielens.org/home', self.site.browser.current_url)

    def tearDown(self):
        self.site.kill_browser()
