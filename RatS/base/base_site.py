import logging
import time

import datetime
import json
import os
from configparser import RawConfigParser

from decouple import config
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from RatS.base.base_exceptions import LoginFailedException, SiteNotReachableException
from RatS.base.movie_entity import Site
from RatS.utils.browser_handler import BrowserHandler

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "RatS", "exports"))


class BaseSite:
    def __init__(self, args):
        self.args = args

        self.site_name: str = type(self).__name__
        self.site: Site = Site(self.site_name.upper())

        self.config = RawConfigParser()
        self.__read_config_file("credentials.cfg.orig")
        self.__read_config_file("credentials.cfg")
        self._parse_credentials()
        self.CREDENTIALS_VALID = self._validate_credentials()

        if self.CREDENTIALS_VALID:
            self.LOGIN_PAGE: str = self._get_login_page_url()

            self._init_browser()

            self._parse_configuration()

    def __read_config_file(self, filename: str):
        self.config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, filename)))

    def _parse_credentials(self):
        self.USERNAME: str = config(
            self.site_name.upper() + "_USERNAME", default=self.config[self.site_name]["USERNAME"]
        )
        self.PASSWORD: str = config(
            self.site_name.upper() + "_PASSWORD", default=self.config[self.site_name]["PASSWORD"]
        )

    def _validate_credentials(self):
        return (
            self.USERNAME
            and self.PASSWORD
            and self.USERNAME != "abc"
            and self.USERNAME != "abc@def.de"
            and self.PASSWORD != "def"
        )

    def _get_login_page_url(self):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_configuration(self):
        # this method should be overwritten by a site, if there are more configs to parse than just the credentials
        # and for things which need a running browser
        pass

    def _init_browser(self):
        self.browser_handler = BrowserHandler(self.args)
        self.browser = self.browser_handler.browser
        self.login()

    def login(self):
        logging.info(f"===== {self.site_name}: performing login")
        self.open_url_with_521_retry(self.LOGIN_PAGE)
        time.sleep(1)

        self._handle_cookie_notice_if_present()
        self._pre_login_action()

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
            self._handle_captcha_challenge_if_present()
            if iteration > 2:
                self._handle_login_unsuccessful()

    def _pre_login_action(self):
        # to be implemented for sites individually
        pass

    def _handle_cookie_notice_if_present(self):
        # to be implemented for sites with cookie banners individually
        pass

    def _handle_captcha_challenge_if_present(self):
        # to be implemented for sites with captchas individually
        pass

    def _handle_login_unsuccessful(self):
        time.sleep(1)
        if self._user_is_not_logged_in():
            self.browser_handler.kill()
            raise LoginFailedException(
                f"Login to {self.site_name} failed. - "
                "Please check if the credentials are correctly set in your credentials.cfg"
            )

    def _user_is_not_logged_in(self):
        return (
            len(self.browser.find_elements(By.XPATH, self.LOGIN_BUTTON_SELECTOR)) > 0
            and len(self.browser.find_elements(By.XPATH, self.LOGIN_USERNAME_SELECTOR)) > 0
            and len(self.browser.find_elements(By.XPATH, self.LOGIN_PASSWORD_SELECTOR)) > 0
        )

    def _insert_login_credentials(self):
        login_field_user = self.browser.find_element(By.XPATH, self.LOGIN_USERNAME_SELECTOR)
        login_field_user.clear()
        login_field_user.send_keys(self.USERNAME)
        login_field_password = self.browser.find_element(By.XPATH, self.LOGIN_PASSWORD_SELECTOR)
        login_field_password.clear()
        login_field_password.send_keys(self.PASSWORD)

    def _click_login_button(self):
        login_button = self.browser.find_element(By.XPATH, self.LOGIN_BUTTON_SELECTOR)
        login_button.click()
        time.sleep(2)  # wait for page to load

    def get_json_from_html(self):
        response = self.browser.find_element(By.TAG_NAME, "pre").text.strip()
        return json.loads(response)

    def open_url_with_521_retry(self, url: str):
        iteration = 0
        self.browser.get(url)

        while len(self.browser.find_elements(By.ID, "cf-error-details")) > 0:
            if iteration >= 10:
                raise SiteNotReachableException
            iteration += 1
            self.browser.get(url)
