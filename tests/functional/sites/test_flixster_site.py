from unittest import TestCase
from unittest import skip

from RatS.flixster.flixster_site import Flixster


@skip('this test is unstable on travis')
class FlixsterSiteTest(TestCase):
    def setUp(self):
        self.site = Flixster(None)

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
