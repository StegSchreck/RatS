from RatS.base.base_site import Site
from RatS.icheckmovies.icheckmovies_misconfiguration_exception import (
    ICheckMoviesMisconfigurationException,
)


class ICheckMovies(Site):
    def __init__(self, args):
        login_form_selector = "//form[@id='login']"
        self.LOGIN_USERNAME_SELECTOR = (
            login_form_selector + "//input[@id='loginUsername']"
        )
        self.LOGIN_PASSWORD_SELECTOR = (
            login_form_selector + "//input[@id='loginPassword']"
        )
        self.LOGIN_BUTTON_SELECTOR = login_form_selector + "//button[@type='submit']"
        super(ICheckMovies, self).__init__(args)
        self.MY_RATINGS_URL = "https://www.icheckmovies.com/movies/favorited/"
        self.MY_RATINGS_URL_FAVORITED = "https://www.icheckmovies.com/movies/favorited/"
        self.MY_RATINGS_URL_DISLIKED = "https://www.icheckmovies.com/movies/disliked/"

    def _get_login_page_url(self):
        return "https://www.icheckmovies.com/login/"

    def _parse_configuration(self):
        self.INSERT_LIKE_LOWER_BOUND = self.config[self.site_name][
            "INSERT_LIKE_LOWER_BOUND"
        ]
        self.INSERT_DISLIKE_UPPER_BOUND = self.config[self.site_name][
            "INSERT_DISLIKE_UPPER_BOUND"
        ]
        self.PARSE_LIKE_TRANSLATION = self.config[self.site_name][
            "PARSE_LIKE_TRANSLATION"
        ]
        self.PARSE_DISLIKE_TRANSLATION = self.config[self.site_name][
            "PARSE_DISLIKE_TRANSLATION"
        ]

        if self.INSERT_LIKE_LOWER_BOUND < self.INSERT_DISLIKE_UPPER_BOUND:
            self.browser_handler.kill()
            raise ICheckMoviesMisconfigurationException(
                "Ambiguous configuration values for iCheckMovies: "
                f"INSERT_DISLIKE_UPPER_BOUND [{self.INSERT_DISLIKE_UPPER_BOUND}] should be lower than"
                f" INSERT_LIKE_LOWER_BOUND [{self.INSERT_LIKE_LOWER_BOUND}], but isn't."
            )

        if self.PARSE_LIKE_TRANSLATION < self.PARSE_DISLIKE_TRANSLATION:
            self.browser_handler.kill()
            raise ICheckMoviesMisconfigurationException(
                "Illogical configuration values for iCheckMovies: "
                f"PARSE_DISLIKE_TRANSLATION [{self.PARSE_DISLIKE_TRANSLATION}] should be lower than"
                f" PARSE_LIKE_TRANSLATION [{self.PARSE_LIKE_TRANSLATION}], but isn't."
            )
