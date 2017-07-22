from RatS.sites.base_site import Site


class Metacritic(Site):
    def __init__(self, args):
        self.LOGIN_PAGE = "https://secure.metacritic.com/login"
        self.LOGIN_USERNAME_SELECTOR = "//form//input[@id='login_email']"
        self.LOGIN_PASSWORD_SELECTOR = "//form//input[@id='login_password']"
        self.LOGIN_BUTTON_SELECTOR = "//form//button[@type='submit']"
        super(Metacritic, self).__init__(args)
        self.MY_RATINGS_URL = ''
