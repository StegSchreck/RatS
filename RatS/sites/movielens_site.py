from RatS.sites.base_site import Site


class Movielens(Site):
    def __init__(self):
        self.LOGIN_PAGE = "https://movielens.org/login"
        self.LOGIN_USERNAME_SELECTOR = "//form//input[@id='inputEmail']"
        self.LOGIN_PASSWORD_SELECTOR = "//form//input[@id='inputPassword']"
        self.LOGIN_BUTTON_SELECTOR = "//form//button[@type='submit']"
        super(Movielens, self).__init__()
        self.MY_RATINGS_URL = 'https://movielens.org/api/movies/explore?hasRated=yes&sortBy=userRatedDate'
