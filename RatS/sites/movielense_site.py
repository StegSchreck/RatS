from RatS.sites.base_site import Site


class Movielense(Site):
    def __init__(self):
        super(Movielense, self).__init__()
        self.MY_RATINGS_URL = 'https://movielens.org/explore/your-ratings'
