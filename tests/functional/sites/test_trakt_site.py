from unittest import TestCase
from unittest import skip

from RatS.sites.trakt_site import Trakt


@skip('this test is unstable on travis')
class TraktSiteTest(TestCase):
    def setUp(self):
        self.site = Trakt()

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.kill_browser()
