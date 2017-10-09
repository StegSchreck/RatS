from RatS.base.base_site import Site


class Letterboxd(Site):
    def __init__(self, args):
        self.LOGIN_PAGE = "https://letterboxd.com/sign-in/"
        login_form_selector = "//form[@id='signin-form']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='signin-username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='signin-password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(Letterboxd, self).__init__(args)
        self.MY_RATINGS_URL = 'https://letterboxd.com/%s/films/ratings/' % self.USERNAME
