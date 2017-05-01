from RatS.sites.base_site import Site


class Letterboxd(Site):
    def __init__(self):
        self.LOGIN_PAGE = "https://letterboxd.com/sign-in/"
        self.LOGIN_USERNAME_SELECTOR = "//form[@id='signin-form']//input[@id='signin-username']"
        self.LOGIN_PASSWORD_SELECTOR = "//form[@id='signin-form']//input[@id='signin-password']"
        self.LOGIN_BUTTON_SELECTOR = "//form[@id='signin-form']//input[@type='submit']"
        super(Letterboxd, self).__init__()
        self.MY_RATINGS_URL = 'https://letterboxd.com/%s/films/ratings/' % self.USERNAME
