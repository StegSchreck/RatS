from unittest import TestCase

from selenium.webdriver import PhantomJS

from RatS.sites.movielense_site import Movielense


class MovielenseSiteTest(TestCase):
    def setUp(self):
        self.site = Movielense()
        self.browser = PhantomJS()

    def test_login(self):
        self.site.login(self.browser)
        self.assertEqual('https://movielens.org/home', self.browser.current_url)

    def tearDown(self):
        self.browser.quit()
