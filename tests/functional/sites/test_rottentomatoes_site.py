from unittest import TestCase
from unittest import skip

from RatS.rottentomatoes.rottentomatoes_site import RottenTomatoes


@skip("this test is unstable on CI")
class RottenTomatoesSiteTest(TestCase):
    def setUp(self):
        self.site = RottenTomatoes(None)

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
