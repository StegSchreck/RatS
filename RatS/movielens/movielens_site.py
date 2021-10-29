from RatS.base.base_site import Site


class Movielens(Site):
    def __init__(self, args):
        login_form_selector = "//form"
        self.LOGIN_USERNAME_SELECTOR = (
            login_form_selector + "//input[@formcontrolname='userName']"
        )
        self.LOGIN_PASSWORD_SELECTOR = (
            login_form_selector + "//input[@formcontrolname='password']"
        )
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(Movielens, self).__init__(args)
        self.MY_RATINGS_URL = (
            "https://movielens.org/api/movies/explore?hasRated=yes&sortBy=userRatedDate"
        )

    def _get_login_page_url(self):
        return "https://movielens.org/login"
