from RatS.base.base_site import Site


class Criticker(Site):
    def __init__(self, args):
        self.LOGIN_PAGE = "https://www.criticker.com/signin.php"
        login_form_selector = "//form[@id='si_signinform']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='si_input_uname']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='si_input_pswd']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@id='si_submit']"
        super(Criticker, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.criticker.com/rankings/'
