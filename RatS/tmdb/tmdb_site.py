from RatS.base.base_site import Site


class TMDB(Site):
    def __init__(self, args):
        self.LOGIN_PAGE = "https://www.themoviedb.org/login"
        login_form_selector = "//form[@name='account_login']"
        self.LOGIN_USERNAME_SELECTOR = login_form_selector + "//input[@id='username']"
        self.LOGIN_PASSWORD_SELECTOR = login_form_selector + "//input[@id='password']"
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//input[@type='submit']"
        super(TMDB, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.themoviedb.org/account/{username}/discover/rated/movie'.format(
            username=self.USERNAME
        )
