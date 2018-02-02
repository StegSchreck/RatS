import datetime
import json
import os
import sys
import time
from configparser import ConfigParser

from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver import Firefox, DesiredCapabilities
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from xvfbwrapper import Xvfb

from RatS.utils.bash_color import BashColor
from RatS.utils import command_line

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))


class Site:
    def __init__(self, args):
        self.args = args

        self.site_name = type(self).__name__
        self.site_displayname = BashColor.HEADER + BashColor.BOLD + self.site_name + BashColor.END \
            if sys.stdout.isatty() else self.site_name

        self.config = ConfigParser()
        self.__read_config_file('credentials.cfg.orig')
        self.__read_config_file('credentials.cfg')
        self._parse_credentials()
        self.LOGIN_PAGE = self._get_login_page_url()

        self._init_browser()

        self._parse_configuration()

    def __read_config_file(self, filename):
        self.config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, filename)))

    def _parse_credentials(self):
        if os.environ.get(self.site_name.upper() + '_USERNAME'):
            self.USERNAME = os.environ.get(self.site_name.upper() + '_USERNAME')
        else:
            self.USERNAME = self.config[self.site_name]['USERNAME']
        if os.environ.get(self.site_name.upper() + '_PASSWORD'):
            self.PASSWORD = os.environ.get(self.site_name.upper() + '_PASSWORD')
        else:
            self.PASSWORD = self.config[self.site_name]['PASSWORD']

    def _get_login_page_url(self):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_configuration(self):
        # this method should be overwritten by a site, if there are more configs to parse than just the credentials
        # and for things which need a running browser
        pass

    def _init_browser(self):
        if self.args and not self.args.show_browser:
            self.display = Xvfb()
            self.display.start()

        if self.args and self.args.verbose and self.args.verbose >= 3:
            log_level = 'trace'
        elif self.args and self.args.verbose and self.args.verbose == 2:
            log_level = 'debug'
        elif self.args and self.args.verbose and self.args.verbose == 1:
            log_level = 'info'
        else:
            log_level = 'warn'

        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities["moz:firefoxOptions"] = {
            "log": {
                "level": log_level,
            },
        }

        options = Options()
        options.log.level = log_level

        profile = FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", EXPORTS_FOLDER)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv, application/zip")
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("devtools.jsonview.enabled", False)
        profile.set_preference("media.volume_scale", "0.0")
        # https://github.com/mozilla/geckodriver/issues/858#issuecomment-322512336
        profile.set_preference("dom.file.createInChild", True)

        self.browser = Firefox(
            firefox_profile=profile,
            capabilities=capabilities,
            firefox_options=options,
            log_path="{timestamp}_geckodriver.log".format(timestamp=TIMESTAMP)
        )
        # http://stackoverflow.com/questions/42754877/cant-upload-file-using-selenium-with-python-post-post-session-b90ee4c1-ef51-4  # pylint: disable=line-too-long
        self.browser._is_remote = False  # pylint: disable=protected-access

        self.login()

    def login(self):
        sys.stdout.write('===== {site_displayname}: performing login'.format(site_displayname=self.site_displayname))
        sys.stdout.flush()
        self.browser.get(self.LOGIN_PAGE)
        time.sleep(1)

        iteration = 0
        while self._user_is_not_logged_in():
            iteration += 1
            try:
                self._insert_login_credentials()
                self._click_login_button()
            except NoSuchElementException as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue
            if iteration > 10:
                self._handle_login_unsuccessful()

    def _handle_login_unsuccessful(self):
        time.sleep(1)
        if self._user_is_not_logged_in():
            command_line.error("Login to {site_name} failed.".format(site_name=self.site_name))
            sys.stdout.write("Please check if the credentials are correctly set in your credentials.cfg\r\n")
            sys.stdout.flush()
            self.kill_browser()
            sys.exit(1)

    def _user_is_not_logged_in(self):
        return len(self.browser.find_elements_by_xpath(self.LOGIN_BUTTON_SELECTOR)) > 0 \
               and len(self.browser.find_elements_by_xpath(self.LOGIN_USERNAME_SELECTOR)) > 0 \
               and len(self.browser.find_elements_by_xpath(self.LOGIN_PASSWORD_SELECTOR)) > 0

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
