import os
from configparser import ConfigParser


class Site:
    def __init__(self):
        self.config = ConfigParser()
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

    def login(self, browser):
        raise NotImplementedError("Should have implemented this")
