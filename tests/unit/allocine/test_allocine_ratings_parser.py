import os
from unittest import TestCase
from unittest.mock import patch

from RatS.allocine.allocine_ratings_parser import AlloCineRatingsParser
from RatS.base.movie_entity import Site, Movie, SiteSpecificMovieData

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets"))


class AlloCineRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        with open(os.path.join(TESTDATA_PATH, "allocine", "my_ratings.html"), encoding="UTF-8") as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(
            os.path.join(TESTDATA_PATH, "allocine", "movie_details_page.html"),
            encoding="UTF-8",
        ) as detail_page:
            self.detail_page = detail_page.read()

    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        AlloCineRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_parser.RatingsParser._print_progress_bar")
    @patch("RatS.allocine.allocine_ratings_parser.AlloCineRatingsParser.parse_movie_details_page")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.allocine.allocine_ratings_parser.AlloCine")
    def test_parser(
        self,
        site_mock,
        base_init_mock,
        browser_mock,
        parse_movie_mock,
        progress_print_mock,
    ):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = AlloCineRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.ALLOCINE
        parser.site.site_name = "AlloCine"
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(2, parse_movie_mock.call_count)
        self.assertEqual(2, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual(SiteSpecificMovieData, type(parser.movies[0].site_data[Site.ALLOCINE]))
        self.assertEqual("21189", parser.movies[0].site_data[Site.ALLOCINE].id)
        self.assertEqual(
            "https://www.allocine.fr/film/fichefilm_gen_cfilm=21189.html",
            parser.movies[0].site_data[Site.ALLOCINE].url,
        )

    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.allocine.allocine_ratings_parser.AlloCine")
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = AlloCineRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.ALLOCINE
        parser.site.site_name = "AlloCine"
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = Movie(title="doesn't matter right now")

        parser.parse_movie_details_page(movie)

        self.assertEqual(1999, movie.year)
        self.assertEqual("Fight Club", movie.title)
        self.assertEqual(9, movie.site_data[Site.ALLOCINE].my_rating)
