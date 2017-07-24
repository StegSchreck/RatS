from unittest import TestCase
from unittest import skip

from RatS.metacritic.metacritic_site import Metacritic


@skip('this test is unstable on travis')
class MetacriticSiteTest(TestCase):
    def setUp(self):
        self.site = Metacritic(None)

    def test_login(self):
        self.assertIn('primary_menu_user_profile', self.site.browser.page_source)

    def tearDown(self):
        self.site.kill_browser()
