import time


class Parser:
    def __init__(self, site):
        self.site = site

        self.movies = []
        self.movies_count = 0

        self.site.browser.get(self.site.MY_RATINGS_URL)

    def parse(self):
        try:
            self._parse_ratings()
        except AttributeError:
            time.sleep(1)  # wait a little bit for page to load and try again
            self._parse_ratings()
        self.site.kill_browser()
        return self.movies

    def _parse_ratings(self):
        raise NotImplementedError("Should have implemented this")
