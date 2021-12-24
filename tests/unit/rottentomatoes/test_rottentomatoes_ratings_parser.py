import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.rottentomatoes.rottentomatoes_ratings_parser import (
    RottenTomatoesRatingsParser,
)

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class RottenTomatoesRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        with open(
            os.path.join(TESTDATA_PATH, "rottentomatoes", "my_ratings_last_page.json"),
            encoding="UTF-8",
        ) as my_ratings:
            self.my_ratings = json.loads(my_ratings.read())

    @patch(
        "RatS.rottentomatoes.rottentomatoes_site.RottenTomatoes._user_is_not_logged_in"
    )
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock, login_check_mock):
        login_check_mock.return_value = False
        RottenTomatoesRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch(
        "RatS.rottentomatoes.rottentomatoes_ratings_parser.RottenTomatoes.get_json_from_html"
    )
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.rottentomatoes.rottentomatoes_ratings_parser.RottenTomatoes")
    def test_parser(self, site_mock, base_init_mock, browser_mock, json_mock):
        json_mock.return_value = self.my_ratings
        parser = RottenTomatoesRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.ROTTENTOMATOES
        parser.site.site_name = "RottenTomatoes"
        parser.site.browser = browser_mock

        parser.parse()

        self.assertEqual(20, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual(
            SiteSpecificMovieData, type(parser.movies[0].site_data[Site.ROTTENTOMATOES])
        )
        self.assertEqual("Not My Day", parser.movies[0].title)
        self.assertEqual(2014, parser.movies[0].year)

        self.assertEqual(
            "771362331", parser.movies[0].site_data[Site.ROTTENTOMATOES].id
        )
        self.assertEqual(
            "https://rottentomatoes.com/m/not_my_day_2014",
            parser.movies[0].site_data[Site.ROTTENTOMATOES].url,
        )
        self.assertEqual(8, parser.movies[0].site_data[Site.ROTTENTOMATOES].my_rating)
