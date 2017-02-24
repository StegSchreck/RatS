from unittest import TestCase

from selenium.webdriver import PhantomJS

from RatS.sites.movielense_site import Movielense


class TraktSiteTest(TestCase):
    def setUp(self):
        self.site = Movielense()
        self.browser = PhantomJS()

    def test_login(self):
        self.site.login(self.browser)

    def tearDown(self):
        self.browser.quit()
