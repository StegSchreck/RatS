from unittest import TestCase
from unittest import skip

from RatS.filmtipset.filmtipset_site import Filmtipset


@skip("this test is unstable on CI")
class FilmtipsetSiteTest(TestCase):
    def setUp(self):
        self.site = Filmtipset(None)

    def test_login(self):
        self.assertEqual("https://www.filmtipset.se/", self.site.browser.current_url)

    def tearDown(self):
        self.site.browser_handler.kill()
