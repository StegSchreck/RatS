import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.movie_entity import Site, Movie, SiteSpecificMovieData
from RatS.filmaffinity.filmaffinity_ratings_parser import FilmAffinityRatingsParser

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class FilmAffinityRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        with open(
            os.path.join(TESTDATA_PATH, "filmaffinity", "my_ratings.html"),
            encoding="UTF-8",
        ) as my_ratings:
            self.my_ratings = my_ratings.read()

    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        FilmAffinityRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_parser.RatingsParser._print_progress_bar")
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.filmaffinity.filmaffinity_ratings_parser.FilmAffinity")
    def test_parser(
        self, site_mock, base_init_mock, browser_mock, progress_print_mock
    ):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = FilmAffinityRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.FILMAFFINITY
        parser.site.site_name = "FilmAffinity"
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(20, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual(
            SiteSpecificMovieData, type(parser.movies[0].site_data[Site.FILMAFFINITY])
        )
        self.assertEqual("Vollidiot", parser.movies[0].title)
        self.assertEqual("125089", parser.movies[0].site_data[Site.FILMAFFINITY].id)
        self.assertEqual(
            "https://www.filmaffinity.com/us/film125089.html",
            parser.movies[0].site_data[Site.FILMAFFINITY].url,
        )
        self.assertEqual(2007, parser.movies[0].year)
        self.assertEqual(7, parser.movies[0].site_data[Site.FILMAFFINITY].my_rating)
