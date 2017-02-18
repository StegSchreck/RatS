from RatS.sites.base_site import Site


class Movielense(Site):
    def __init__(self):
        self.LOGIN_PAGE = 'https://movielens.org/login'
        self.MY_RATINGS_URL = 'https://movielens.org/explore/your-ratings'
        super(Movielense, self).__init__()

    def login(self, browser):
        pass
