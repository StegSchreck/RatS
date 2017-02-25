from selenium.webdriver import PhantomJS


class Inserter:
    def __init__(self, site):
        self.site = site

        self.browser = PhantomJS()
        self.site.login(self.browser)
        self.browser.set_page_load_timeout(10)
        self.browser.set_script_timeout(10)

    def insert(self, movies):
        raise NotImplementedError("Should have implemented this")
