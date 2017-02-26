import os
import time
from configparser import ConfigParser

import sys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import PhantomJS


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

        self.browser = PhantomJS()
        self.login()

    def login(self):
        sys.stdout.write('===== %s: login =====\r\n' % type(self).__name__)
        sys.stdout.flush()
        self.browser.get(self.LOGIN_PAGE)
        time.sleep(1)

        try:
            self._insert_login_credentials()
            self._click_login_button()
        except NoSuchElementException:
            time.sleep(2)  # wait for page to load and try again
            self._insert_login_credentials()
            self._click_login_button()

    def _insert_login_credentials(self):
        raise NotImplementedError("Should have implemented this")

    def _click_login_button(self):
        login_button = self.browser.find_element_by_xpath(self.LOGIN_BUTTON_SELECTOR)
        login_button.click()
        time.sleep(2)  # wait for page to load

    def kill_browser(self):
        self.browser.stop_client()
        self.browser.close()
        self.browser.quit()
