from RatS.base.base_site import Site


class FilmAffinity(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='login-form']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@name='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@name='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(FilmAffinity, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.filmaffinity.com/en/myvotes.php'

    def _get_login_page_url(self):
        return "https://www.filmaffinity.com/en/login.php"
