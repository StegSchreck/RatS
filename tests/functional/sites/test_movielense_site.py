import os
from unittest import TestCase

from selenium.webdriver import PhantomJS

from RatS.sites.movielense import Movielense


class TraktSiteTest(TestCase):
    def setUp(self):
        self.site = Movielense()
        site_type = type(self.site).__name__.upper()
        if os.environ.get(site_type + '_USERNAME'):
            self.site.USERNAME = os.environ.get(site_type + '_USERNAME')
        if os.environ.get(site_type + '_PASSWORD'):
            self.site.PASSWORD = os.environ.get(site_type + '_PASSWORD')
        self.browser = PhantomJS()

    def test_login(self):
        self.site.login(self.browser)

    def tearDown(self):
        self.browser.quit()
