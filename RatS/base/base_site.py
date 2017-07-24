import json
import os
import sys
import time
from configparser import ConfigParser

from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxProfile
from xvfbwrapper import Xvfb

EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))


class Site:
    def __init__(self, args):
        self.args = args

        self.config = ConfigParser()
        self.config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'credentials.cfg.orig')))
        self.config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'credentials.cfg')))
        self.site_name = type(self).__name__
        if os.environ.get(self.site_name.upper() + '_USERNAME'):
            self.USERNAME = os.environ.get(self.site_name.upper() + '_USERNAME')
        else:
            self.USERNAME = self.config[self.site_name]['USERNAME']
        if os.environ.get(self.site_name.upper() + '_PASSWORD'):
            self.PASSWORD = os.environ.get(self.site_name.upper() + '_PASSWORD')
        else:
            self.PASSWORD = self.config[self.site_name]['PASSWORD']

        self._init_browser()

    def _init_browser(self):
        if self.args and not self.args.show_browser:
            self.display = Xvfb()
            self.display.start()

        profile = FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", EXPORTS_FOLDER)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv, application/zip")
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("devtools.jsonview.enabled", False)
        profile.set_preference("media.volume_scale", "0.0")

        self.browser = Firefox(firefox_profile=profile)
        # http://stackoverflow.com/questions/42754877/cant-upload-file-using-selenium-with-python-post-post-session-b90ee4c1-ef51-4  # pylint: disable=line-too-long
        self.browser._is_remote = False  # pylint: disable=protected-access
        self.login()
        time.sleep(1)

    def login(self):
        sys.stdout.write('===== %s: performing login' % type(self).__name__)
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
        login_field_user = self.browser.find_element_by_xpath(self.LOGIN_USERNAME_SELECTOR)
        login_field_user.send_keys(self.USERNAME)
        login_field_password = self.browser.find_element_by_xpath(self.LOGIN_PASSWORD_SELECTOR)
        login_field_password.send_keys(self.PASSWORD)

    def _click_login_button(self):
        login_button = self.browser.find_element_by_xpath(self.LOGIN_BUTTON_SELECTOR)
        login_button.click()
        time.sleep(2)  # wait for page to load

    def kill_browser(self):
        self.browser.stop_client()
        self.browser.close()
        try:
            self.browser.quit()
        except WebDriverException:
            pass

        if self.args and not self.args.show_browser:
            self.display.stop()

    def get_json_from_html(self):
        response = self.browser.find_element_by_tag_name("pre").text.strip()
        return json.loads(response)
