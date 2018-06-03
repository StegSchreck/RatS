from unittest import TestCase
from unittest import skip

from RatS.icheckmovies.icheckmovies_site import ICheckMovies


@skip('this test is unstable on travis')
class ICheckMoviesSiteTest(TestCase):
    def setUp(self):
        self.site = ICheckMovies(None)

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
