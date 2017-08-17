from RatS.base.base_site import Site


class ICheckMovies(Site):
    def __init__(self, args):
        self.LOGIN_PAGE = "https://www.icheckmovies.com/login/"
        self.LOGIN_USERNAME_SELECTOR = "//form[@id='login']//input[@id='loginUsername']"
        self.LOGIN_PASSWORD_SELECTOR = "//form[@id='login']//input[@id='loginPassword']"
        self.LOGIN_BUTTON_SELECTOR = "//form[@id='login']//button[@type='submit']"
        super(ICheckMovies, self).__init__(args)
        self.MY_RATINGS_URL = 'https://www.icheckmovies.com/movies/favorited/'
        self.MY_RATINGS_URL_FAVORITED = 'https://www.icheckmovies.com/movies/favorited/'
        self.MY_RATINGS_URL_DISLIKED = 'https://www.icheckmovies.com/movies/disliked/'
        self.INSERT_LIKE_LOWER_BOUND = self.config[self.site_name]['INSERT_LIKE_LOWER_BOUND']
        self.INSERT_DISLIKE_UPPER_BOUND = self.config[self.site_name]['INSERT_DISLIKE_UPPER_BOUND']
        self.PARSE_LIKE_TRANSLATION = self.config[self.site_name]['PARSE_LIKE_TRANSLATION']
        self.PARSE_DISLIKE_TRANSLATION = self.config[self.site_name]['PARSE_DISLIKE_TRANSLATION']
