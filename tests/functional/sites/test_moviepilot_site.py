from unittest import TestCase
from unittest import skip

from RatS.moviepilot.moviepilot_site import MoviePilot


@skip('this test is unstable on travis')
class MoviePilotSiteTest(TestCase):
    def setUp(self):
        self.site = MoviePilot(None)

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
