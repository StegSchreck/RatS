from unittest import TestCase
from unittest import skip

from RatS.imdb.imdb_site import IMDB


@skip('this test is unstable on travis')
class IMDBSiteTest(TestCase):
    def setUp(self):
        self.site = IMDB(None)

    def test_login(self):
        self.assertIn('imdb.com', self.site.browser.current_url)
        self.assertNotIn('Sign in', self.site.browser.page_source)

    def tearDown(self):
        self.site.browser_handler.kill()
