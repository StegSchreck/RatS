import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.listal.listal_ratings_parser import ListalRatingsParser

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class ListalParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        with open(
            os.path.join(TESTDATA_PATH, "listal", "my_ratings.html"), encoding="UTF-8"
        ) as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(
            os.path.join(TESTDATA_PATH, "listal", "movie_details_page.html"),
            encoding="UTF-8",
        ) as detail_page:
            self.detail_page = detail_page.read()

    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        ListalRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_parser.RatingsParser._print_progress_bar")
    @patch(
        "RatS.listal.listal_ratings_parser.ListalRatingsParser.parse_movie_details_page"
    )
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.listal.listal_ratings_parser.Listal")
    def test_parser(
        self,
        site_mock,
        base_init_mock,
        browser_mock,
        parse_movie_mock,
        progress_print_mock,
    ):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = ListalRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.LISTAL
        parser.site.site_name = "Listal"
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(60, parse_movie_mock.call_count)
        self.assertEqual(60, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual(SiteSpecificMovieData, type(parser.movies[0].site_data[parser.site.site]))
        self.assertEqual("Fight Club", parser.movies[0].title)
        self.assertEqual("1596", parser.movies[0].site_date[Site.LISTAL].id)
        self.assertEqual(
            "https://www.listal.com/movie/fight-club", parser.movies[0].site_date[Site.LISTAL].url
        )

    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.listal.listal_ratings_parser.Listal")
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = ListalRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.LISTAL
        parser.site.site_name = "Listal"
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = Movie()

        parser.parse_movie_details_page(movie)

        self.assertEqual(1999, movie.year)
        self.assertEqual(10, movie.site_data[Site.LISTAL].my_rating)
        self.assertEqual("tt0137523", movie.site_data[Site.IMDB].id)
        self.assertEqual(
            "https://www.imdb.com/title/tt0137523", movie.site_data[Site.IMDB].url
        )
