class Inserter:
    def __init__(self, site):
        self.site = site
        self.failed_movies = []
        self.site_name = type(self.site).__name__

    def insert(self, movies, source):
        raise NotImplementedError("Should have implemented this")
