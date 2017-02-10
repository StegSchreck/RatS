import abc
import os
from configparser import ConfigParser

from selenium import webdriver


class BaseParser:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(os.path.dirname(__file__) + '/credentials.cfg')

        self.movies = []

        self.browser = webdriver.PhantomJS()
        self.login()

        self.LOGIN_PAGE = ''

    def login(self):
        self.browser.get(self.LOGIN_PAGE)

        self._insert_login_credentials()
        self._click_login_button()

    def _click_login_button(self):
        raise NotImplementedError("Should have implemented this")

    def _insert_login_credentials(self):
        raise NotImplementedError("Should have implemented this")

    def parse(self):
        raise NotImplementedError("Should have implemented this")
