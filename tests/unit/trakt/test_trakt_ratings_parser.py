import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.movie_entity import Site, Movie, SiteSpecificMovieData
from RatS.trakt.trakt_ratings_parser import TraktRatingsParser

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class TraktRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        with open(
            os.path.join(TESTDATA_PATH, "trakt", "my_ratings.html"), encoding="UTF-8"
        ) as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(
            os.path.join(TESTDATA_PATH, "trakt", "movie_details_page.html"),
            encoding="UTF-8",
        ) as detail_page:
            self.detail_page = detail_page.read()
        with open(
            os.path.join(
                TESTDATA_PATH, "trakt", "movie_details_page_missing_imdb_id.html"
            ),
            encoding="UTF-8",
        ) as detail_page_without_imdb_id:
            self.detail_page_without_imdb_id = detail_page_without_imdb_id.read()

    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        TraktRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_parser.RatingsParser._print_progress_bar")
    @patch(
        "RatS.trakt.trakt_ratings_parser.TraktRatingsParser.parse_movie_details_page"
    )
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.trakt.trakt_ratings_parser.Trakt")
    def test_parser(
        self,
        site_mock,
        base_init_mock,
        browser_mock,
        parse_movie_mock,
        progress_print_mock,
    ):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.TRAKT
        parser.site.site_name = "Trakt"
        parser.site.browser = browser_mock
        parser.args = None

        parser.parse()

        self.assertEqual(60, parse_movie_mock.call_count)
        self.assertEqual(60, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual(
            SiteSpecificMovieData, type(parser.movies[0].site_data[Site.TRAKT])
        )
        self.assertEqual("Arrival", parser.movies[0].title)
        self.assertEqual("210803", parser.movies[0].site_data[Site.TRAKT].id)
        self.assertEqual(
            "https://trakt.tv/movies/arrival-2016",
            parser.movies[0].site_data[Site.TRAKT].url,
        )

    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.trakt.trakt_ratings_parser.Trakt")
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.TRAKT
        parser.site.site_name = "Trakt"
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = Movie(title="doesn't matter right now")

        parser.parse_movie_details_page(movie)

        # Fight Club
        self.assertEqual(1999, movie.year)
        self.assertEqual("tt0137523", movie.site_data[Site.IMDB].id)
        self.assertEqual(
            "https://www.imdb.com/title/tt0137523", movie.site_data[Site.IMDB].url
        )
        self.assertEqual("550", movie.site_data[Site.TMDB].id)
        self.assertEqual(
            "https://www.themoviedb.org/movie/550", movie.site_data[Site.TMDB].url
        )
        self.assertEqual(10, int(movie.site_data[Site.TRAKT].my_rating))

    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.trakt.trakt_ratings_parser.Trakt")
    def test_parser_single_movie_with_missing_imdb_id(
        self, site_mock, base_init_mock, browser_mock
    ):
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.TRAKT
        parser.site.site_name = "Trakt"
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page_without_imdb_id
        movie = Movie(title="doesn't matter right now")

        parser.parse_movie_details_page(movie)

        # Top Gear Patagonia
        self.assertEqual(2014, movie.year)
        self.assertNotIn(Site.IMDB, movie.site_data.keys())
        self.assertIn(Site.TMDB, movie.site_data.keys())
        self.assertEqual("314390", movie.site_data[Site.TMDB].id)
        self.assertEqual(
            "https://www.themoviedb.org/movie/314390", movie.site_data[Site.TMDB].url
        )
        self.assertEqual(8, movie.site_data[Site.TRAKT].my_rating)
