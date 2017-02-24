import os
from configparser import ConfigParser


class Site:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'credentials.cfg.orig')))
        self.config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'credentials.cfg')))
        site_name = type(self).__name__
        if os.environ.get(site_name.upper() + '_USERNAME'):
            self.USERNAME = os.environ.get(site_name.upper() + '_USERNAME')
        else:
            self.USERNAME = self.config[site_name]['USERNAME']
        if os.environ.get(site_name.upper() + '_PASSWORD'):
            self.PASSWORD = os.environ.get(site_name.upper() + '_PASSWORD')
        else:
            self.PASSWORD = self.config[site_name]['PASSWORD']
        self.LOGIN_PAGE = self.config[site_name]['LOGIN_PAGE']
        self.LOGIN_BUTTON_SELECTOR = self.config[site_name]['LOGIN_BUTTON_SELECTOR']

    def login(self, browser):
        browser.get(self.LOGIN_PAGE)

        self._insert_login_credentials(browser)
        self._click_login_button(browser)

    def _insert_login_credentials(self, browser):
        raise NotImplementedError("Should have implemented this")

    def _click_login_button(self, browser):
        login_button = browser.find_element_by_xpath(self.LOGIN_BUTTON_SELECTOR)
        login_button.click()
