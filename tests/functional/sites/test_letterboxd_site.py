from unittest import TestCase
from unittest import skip

from RatS.letterboxd.letterboxd_site import Letterboxd


@skip('this test is unstable on travis')
class LetterboxdSiteTest(TestCase):
    def setUp(self):
        self.site = Letterboxd(None)

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
