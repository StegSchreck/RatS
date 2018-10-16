from RatS.base.base_site import Site


class Letterboxd(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='signin-form']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='signin-username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='signin-password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(Letterboxd, self).__init__(args)
        self.MY_RATINGS_URL = 'https://letterboxd.com/{username}/films/ratings/'.format(username=self.USERNAME)

    def _get_login_page_url(self):
        return "https://letterboxd.com/sign-in/"

    def _user_is_not_logged_in(self):
        return self.USERNAME not in self.browser.page_source
