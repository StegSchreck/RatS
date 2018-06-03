from unittest import TestCase
from unittest import skip

from RatS.movielens.movielens_site import Movielens


@skip('this test is unstable on travis')
class MovielensSiteTest(TestCase):
    def setUp(self):
        self.site = Movielens(None)

    def test_login(self):
        self.assertEqual('https://movielens.org/home', self.site.browser.current_url)

    def tearDown(self):
        self.site.browser_handler.kill()
