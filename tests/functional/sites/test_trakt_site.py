import os
from unittest import TestCase

from selenium.webdriver import PhantomJS

from RatS.sites.trakt import Trakt


class TraktSiteTest(TestCase):
    def setUp(self):
        self.site = Trakt()
        site_type = type(self.site).__name__.upper()
        if os.environ.get(site_type + '_USERNAME'):
            self.site.USERNAME = os.environ.get(site_type + '_USERNAME')
        if os.environ.get(site_type + '_PASSWORD'):
            self.site.PASSWORD = os.environ.get(site_type + '_PASSWORD')
        self.browser = PhantomJS()

    def test_login(self):
        self.site.login(self.browser)
        self.assertIn(self.site.USERNAME, self.browser.page_source)

    def tearDown(self):
        self.browser.quit()
