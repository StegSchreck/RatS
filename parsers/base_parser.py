from selenium import webdriver


class Parser:
    def __init__(self, site):
        self.site = site

        self.movies = []

        self.browser = webdriver.PhantomJS()
        self.site.login(self.browser)

    def parse(self):
        raise NotImplementedError("Should have implemented this")
