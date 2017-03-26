from RatS.sites.base_site import Site


class TMDB(Site):
    def __init__(self):
        self.LOGIN_PAGE = "https://www.themoviedb.org/login"
        self.LOGIN_USERNAME_SELECTOR = "//form[@name='account_login']//input[@id='username']"
        self.LOGIN_PASSWORD_SELECTOR = "//form[@name='account_login']//input[@id='password']"
        self.LOGIN_BUTTON_SELECTOR = "//form[@name='account_login']//input[@type='submit']"
        super(TMDB, self).__init__()
        self.MY_RATINGS_URL = 'https://www.themoviedb.org/account/%s/discover/rated/movies' % self.USERNAME
