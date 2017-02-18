from selenium.webdriver import PhantomJS


class Parser:
    def __init__(self, site):
        self.site = site

        self.movies = []

        self.browser = PhantomJS()
        self.site.login(self.browser)
        self.browser.get(self.site.MY_RATINGS_URL)

    def parse(self):
        raise NotImplementedError("Should have implemented this")

    def kill_browser(self):
        self.browser.stop_client()
        self.browser.close()
        self.browser.quit()
