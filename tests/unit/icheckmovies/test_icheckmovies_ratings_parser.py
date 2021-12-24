import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.movie_entity import Site, Movie, SiteSpecificMovieData
from RatS.icheckmovies.icheckmovies_ratings_parser import ICheckMoviesRatingsParser

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class ICheckMoviesParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        with open(
            os.path.join(TESTDATA_PATH, "icheckmovies", "my_ratings_like.html"),
            encoding="UTF-8",
        ) as my_ratings_like:
            self.my_ratings_like = my_ratings_like.read()
        with open(
            os.path.join(TESTDATA_PATH, "icheckmovies", "my_ratings_dislike.html"),
            encoding="UTF-8",
        ) as my_ratings_dislike:
            self.my_ratings_dislike = my_ratings_dislike.read()

    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        ICheckMoviesRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_parser.RatingsParser._print_progress_bar")
    @patch(
        "RatS.icheckmovies.icheckmovies_ratings_parser.ICheckMoviesRatingsParser._parse_movies_category"
    )
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.icheckmovies.icheckmovies_ratings_parser.ICheckMovies")
    def test_parser(
        self,
        site_mock,
        base_init_mock,
        browser_mock,
        parse_category_mock,
        progress_print_mock,
    ):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings_like
        parser = ICheckMoviesRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = "ICheckMovies"
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(2, parse_category_mock.call_count)

    @patch("RatS.base.base_ratings_parser.RatingsParser._print_progress_bar")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.icheckmovies.icheckmovies_ratings_parser.ICheckMovies")
    def test_parser_likes(
        self, site_mock, base_init_mock, browser_mock, progress_print_mock
    ):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings_like
        site_mock.PARSE_LIKE_TRANSLATION = 8
        site_mock.PARSE_DISLIKE_TRANSLATION = 3
        parser = ICheckMoviesRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.ICHECKMOVIES
        parser.site.site_name = "ICheckMovies"
        parser.site.browser = browser_mock
        parser.args = None

        parser._parse_movies_category(
            "mock-url", "like"
        )  # pylint: disable=protected-access

        self.assertEqual(240, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual(
            SiteSpecificMovieData, type(parser.movies[0].site_data[Site.ICHECKMOVIES])
        )
        self.assertEqual("Fight Club", parser.movies[0].title)
        self.assertEqual("21", parser.movies[0].site_data[Site.ICHECKMOVIES].id)
        self.assertEqual(
            "https://www.icheckmovies.com/movies/fight+club/",
            parser.movies[0].site_data[Site.ICHECKMOVIES].url,
        )
        self.assertEqual(1999, parser.movies[0].year)
        self.assertEqual(
            SiteSpecificMovieData, type(parser.movies[0].site_data[Site.IMDB])
        )
        self.assertEqual("tt0137523", parser.movies[0].site_data[Site.IMDB].id)
        self.assertEqual(
            "https://www.imdb.com/title/tt0137523",
            parser.movies[0].site_data[Site.IMDB].url,
        )
        self.assertEqual(8, parser.movies[0].site_data[Site.ICHECKMOVIES].my_rating)

    @patch("RatS.base.base_ratings_parser.RatingsParser._print_progress_bar")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.icheckmovies.icheckmovies_ratings_parser.ICheckMovies")
    def test_parser_dislikes(
        self, site_mock, base_init_mock, browser_mock, progress_print_mock
    ):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings_dislike
        site_mock.PARSE_LIKE_TRANSLATION = 8
        site_mock.PARSE_DISLIKE_TRANSLATION = 3
        parser = ICheckMoviesRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.ICHECKMOVIES
        parser.site.site_name = "ICheckMovies"
        parser.site.browser = browser_mock
        parser.args = None

        parser._parse_movies_category(
            "mock-url", "dislike"
        )  # pylint: disable=protected-access

        self.assertEqual(25, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual(
            SiteSpecificMovieData, type(parser.movies[0].site_data[Site.ICHECKMOVIES])
        )
        self.assertEqual("Daniel der Zauberer", parser.movies[0].title)
        self.assertEqual("119234", parser.movies[0].site_data[Site.ICHECKMOVIES].id)
        self.assertEqual(
            "https://www.icheckmovies.com/movies/daniel+der+zauberer/",
            parser.movies[0].site_data[Site.ICHECKMOVIES].url,
        )
        self.assertEqual(2004, parser.movies[0].year)
        self.assertEqual(
            SiteSpecificMovieData, type(parser.movies[0].site_data[Site.ICHECKMOVIES])
        )
        self.assertEqual("tt0421051", parser.movies[0].site_data[Site.IMDB].id)
        self.assertEqual(
            "https://www.imdb.com/title/tt0421051",
            parser.movies[0].site_data[Site.IMDB].url,
        )
        self.assertEqual(3, parser.movies[0].site_data[Site.ICHECKMOVIES].my_rating)
