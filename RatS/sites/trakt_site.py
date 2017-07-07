from RatS.sites.base_site import Site


class Trakt(Site):
    def __init__(self, args):
        self.LOGIN_PAGE = "https://trakt.tv/auth/signin"
        self.LOGIN_USERNAME_SELECTOR = "//form[@id='new_user']//input[@id='user_login']"
        self.LOGIN_PASSWORD_SELECTOR = "//form[@id='new_user']//input[@id='user_password']"
        self.LOGIN_BUTTON_SELECTOR = "//form[@id='new_user']//input[@type='submit']"
        super(Trakt, self).__init__(args)
        self.MY_RATINGS_URL = 'https://trakt.tv/users/%s/ratings/movies/all/added' % self.USERNAME
