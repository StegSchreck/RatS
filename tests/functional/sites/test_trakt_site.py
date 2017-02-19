from unittest import TestCase

from selenium.webdriver import PhantomJS

from RatS.sites.trakt import Trakt


class TraktSiteTest(TestCase):
    def setUp(self):
        self.site = Trakt()
        self.browser = PhantomJS()

    def test_login(self):
        self.site.login(self.browser)
        self.assertIn(self.site.USERNAME, self.browser.page_source)

    def tearDown(self):
        self.browser.quit()
