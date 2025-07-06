import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.flixster.flixster_ratings_inserter import FlixsterRatingsInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets"))


class FlixsterRatingsInserterTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        self.movie = Movie(title="Fight Club", year=1999)
        self.movie.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0137523",
            url="https://www.imdb.com/title/tt0137523",
            my_rating=9,
        )
        self.movie.site_data[Site.TMDB] = SiteSpecificMovieData(
            id="550",
            url="https://www.themoviedb.org/movie/550",
        )
        with open(
            os.path.join(TESTDATA_PATH, "flixster", "search_result.html"),
            encoding="ISO-8859-1",
        ) as search_results:
            self.search_results = search_results.read()
        with open(
            os.path.join(TESTDATA_PATH, "flixster", "search_result_tile.html"),
            encoding="ISO-8859-1",
        ) as result_tile:
            self.search_result_tile_list = [result_tile.read()]
        with open(
            os.path.join(TESTDATA_PATH, "flixster", "movie_details_page.html"),
            encoding="ISO-8859-1",
        ) as movie_details_page:
            self.movie_details_page = movie_details_page.read()

    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        FlixsterRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar")
    @patch("RatS.flixster.flixster_ratings_inserter.FlixsterRatingsInserter._is_requested_movie")
    @patch("RatS.flixster.flixster_ratings_inserter.FlixsterRatingsInserter._get_search_results")
    @patch("RatS.flixster.flixster_ratings_inserter.Flixster")
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
        inserter = FlixsterRatingsInserter(None)
        inserter.args = False
        inserter.site = site_mock
        inserter.site.site_name = "Flixster"
        inserter.failed_movies = []

        inserter.insert([self.movie], Site.IMDB)

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch("RatS.flixster.flixster_ratings_inserter.Flixster")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success_by_year(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FlixsterRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Flixster"
        inserter.failed_movies = []

        movie2 = Movie(title="Fight Club", year=1999)
        movie2.site_data[Site.FLIXSTER] = SiteSpecificMovieData(url="https://www.flixster.com/movie/fight-club/")

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.flixster.flixster_ratings_inserter.Flixster")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success_by_own_url(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FlixsterRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Flixster"
        inserter.failed_movies = []

        movie2 = Movie(title="Fight Club", year=1999)

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.flixster.flixster_ratings_inserter.FlixsterRatingsInserter._is_requested_movie")
    @patch("RatS.flixster.flixster_ratings_inserter.FlixsterRatingsInserter._get_search_results")
    @patch("RatS.flixster.flixster_ratings_inserter.Flixster")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_fail(
        self, browser_mock, base_init_mock, site_mock, tiles_mock, equality_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FlixsterRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Flixster"
        inserter.failed_movies = []
        tiles_mock.return_value = self.search_result_tile_list
        equality_mock.return_value = False

        movie2 = Movie(title="The Matrix", year=1995)
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0137523",
            url="https://www.imdb.com/title/tt0137523",
            my_rating=9,
        )

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch("RatS.flixster.flixster_ratings_inserter.FlixsterRatingsInserter._search_for_movie")
    @patch("RatS.flixster.flixster_ratings_inserter.Flixster")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success_directly_at_search(self, browser_mock, base_init_mock, site_mock, search_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FlixsterRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Flixster"
        inserter.failed_movies = []
        search_mock.return_value = True

        movie2 = Movie(title="Fight Club", year=1999)

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.flixster.flixster_ratings_inserter.FlixsterRatingsInserter._is_empty_search_result")
    @patch("RatS.flixster.flixster_ratings_inserter.FlixsterRatingsInserter._search_for_movie")
    @patch("RatS.flixster.flixster_ratings_inserter.Flixster")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_fail_at_search(
        self, browser_mock, base_init_mock, site_mock, search_mock, empty_result_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FlixsterRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Flixster"
        inserter.failed_movies = []
        search_mock.return_value = False
        empty_result_mock.return_value = True

        movie2 = Movie(title="Not A Movie", year=1999)

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)
