from RatS.base.base_site import Site


class Criticker(Site):
    def __init__(self, args):
        login_form_selector = "//form"
        self.LOGIN_USERNAME_SELECTOR = (
            login_form_selector + "//input[@id='si_username']"
        )
        self.LOGIN_PASSWORD_SELECTOR = (
            login_form_selector + "//input[@id='si_password']"
        )
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(Criticker, self).__init__(args)
        self.MY_RATINGS_URL = "https://www.criticker.com/rankings/"

    def _get_login_page_url(self):
        return "https://www.criticker.com/signin.php"
