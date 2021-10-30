import json
import os
from unittest import TestCase
from unittest.mock import patch

from RatS.rottentomatoes.rottentomatoes_ratings_inserter import (
    RottenTomatoesRatingsInserter,
)

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class RottenTomatoesRatingsInserterTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        self.movie = Movie()
        self.movie.title = "Fight Club"
        self.movie.year = 1999
        self.movie.site_data[Site.IMDB] = SiteSpecificMovieData()
        self.movie.site_data[Site.IMDB].id = "tt0137523"
        self.movie.site_data[Site.IMDB]["url"] = "https://www.imdb.com/title/tt0137523"
        self.movie.site_data[Site.IMDB]["my_rating"] = 9
        self.movie["tmdb"] = SiteSpecificMovieData()
        self.movie["tmdb"]["id"] = "550"
        self.movie["tmdb"]["url"] = "https://www.themoviedb.org/movie/550"
        with open(
            os.path.join(TESTDATA_PATH, "rottentomatoes", "search_result.json"),
            encoding="UTF-8",
        ) as search_results:
            self.search_results = json.loads(search_results.read())
        with open(
            os.path.join(TESTDATA_PATH, "rottentomatoes", "search_result_tile.json"),
            encoding="UTF-8",
        ) as result_tile:
            self.search_result_tile_list = [json.loads(result_tile.read())]

    @patch(
        "RatS.rottentomatoes.rottentomatoes_site.RottenTomatoes._user_is_not_logged_in"
    )
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock, login_check_mock):
        login_check_mock.return_value = False
        RottenTomatoesRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar")
    @patch(
        "RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoesRatingsInserter._is_requested_movie"
    )
    @patch(
        "RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoesRatingsInserter._get_search_results"
    )
    @patch("RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoes")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_insert(
        self,
        browser_mock,
        base_init_mock,
        site_mock,
        overview_page_mock,  # pylint: disable=too-many-arguments
        eq_check_mock,
        progress_print_mock,
    ):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = RottenTomatoesRatingsInserter(None)
        inserter.args = False
        inserter.site = site_mock
        inserter.site.site_name = "RottenTomatoes"
        inserter.failed_movies = []

        inserter.insert([self.movie], "IMDB")

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch(
        "RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoesRatingsInserter._get_search_results"
    )
    @patch("RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoes")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success_by_year(
        self, browser_mock, base_init_mock, site_mock, overview_page_mock
    ):  # pylint: disable=too-many-arguments
        overview_page_mock.return_value = self.search_results["movies"]
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = RottenTomatoesRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "RottenTomatoes"
        inserter.failed_movies = []

        result = inserter._find_movie(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch(
        "RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoesRatingsInserter._is_requested_movie"
    )
    @patch(
        "RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoesRatingsInserter._get_search_results"
    )
    @patch("RatS.rottentomatoes.rottentomatoes_ratings_inserter.RottenTomatoes")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_fail(
        self, browser_mock, base_init_mock, site_mock, tiles_mock, equality_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = RottenTomatoesRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "RottenTomatoes"
        inserter.failed_movies = []
        tiles_mock.return_value = self.search_result_tile_list
        equality_mock.return_value = False

        movie2 = Movie()
        movie2["title"] = "The Matrix"
        movie2["year"] = 1995
        movie2["imdb"] = SiteSpecificMovieData()
        movie2["imdb"]["id"] = "tt0137523"
        movie2["imdb"]["url"] = "https://www.imdb.com/title/tt0137523"
        movie2["imdb"]["my_rating"] = 9

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)
