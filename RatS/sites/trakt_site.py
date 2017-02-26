from RatS.sites.base_site import Site


class Trakt(Site):
    def __init__(self):
        super(Trakt, self).__init__()
        self.MY_RATINGS_URL = 'https://trakt.tv/users/%s/ratings/movies/all/added' % self.USERNAME
