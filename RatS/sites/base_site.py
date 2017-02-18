import os
from configparser import ConfigParser


class Site:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'credentials.cfg')))
        self.USERNAME = self.config[type(self).__name__]['USERNAME']
        self.PASSWORD = self.config[type(self).__name__]['PASSWORD']

    def login(self, browser):
        raise NotImplementedError("Should have implemented this")
