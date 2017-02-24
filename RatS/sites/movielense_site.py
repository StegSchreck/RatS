from RatS.sites.base_site import Site


class Movielense(Site):
    def __init__(self):
        self.MY_RATINGS_URL = 'https://movielens.org/explore/your-ratings'
        super(Movielense, self).__init__()

    def _insert_login_credentials(self, browser):
        pass

    def _click_login_button(self, browser):
        pass
