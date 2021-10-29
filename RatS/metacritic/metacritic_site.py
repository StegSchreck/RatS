from RatS.base.base_site import BaseSite


class Metacritic(BaseSite):
    def __init__(self, args):
        login_form_selector = "//form"
        self.LOGIN_USERNAME_SELECTOR = (
            login_form_selector + "//input[@id='login_email']"
        )
        self.LOGIN_PASSWORD_SELECTOR = (
            login_form_selector + "//input[@id='login_password']"
        )
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(Metacritic, self).__init__(args)
        self.MY_RATINGS_URL = ""

    def _get_login_page_url(self):
        return "https://secure.metacritic.com/login"
