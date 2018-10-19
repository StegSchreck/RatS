from unittest import TestCase
from unittest import skip

from RatS.filmaffinity.filmaffinity_site import FilmAffinity


@skip('this test is unstable on travis')
class FilmAffinitySiteTest(TestCase):
    def setUp(self):
        self.site = FilmAffinity(None)

    def test_login(self):
        self.assertIn(self.site.USERNAME, self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
