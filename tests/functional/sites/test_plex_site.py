from unittest import TestCase
from unittest import skip

from RatS.plex.plex_site import Plex


@skip("this test is unstable on CI")
class PlexSiteTest(TestCase):
    def setUp(self):
        self.site = Plex(None)

    def test_login(self):
        self.assertIn("signed-in", self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
