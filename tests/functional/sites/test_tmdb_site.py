from unittest import TestCase
from unittest import skip

from RatS.sites.tmdb_site import TMDB


@skip('this test is unstable on travis')
class TMDBSiteTest(TestCase):
    def setUp(self):
        self.site = TMDB()

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.kill_browser()
