class Parser:
    def __init__(self, site):
        self.site = site

        self.movies = []
        self.movies_count = 0

        self.site.browser.get(self.site.MY_RATINGS_URL)

    def parse(self):
        raise NotImplementedError("Should have implemented this")
