import os
from unittest import TestCase
from unittest.mock import patch

from RatS.base.movie_entity import Movie, SiteSpecificMovieData, Site
from RatS.filmaffinity.filmaffinity_ratings_inserter import FilmAffinityRatingsInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets"))


class FilmAffinityRatingsInserterTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        self.movie = Movie(title="Ghost in the Shell", year=1995)
        self.movie.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0113568",
            url="https://www.imdb.com/title/tt0113568",
            my_rating=9,
        )
        with open(
            os.path.join(TESTDATA_PATH, "filmaffinity", "search_result.html"),
            encoding="UTF-8",
        ) as search_results:
            self.search_results = search_results.read()
        with open(
            os.path.join(TESTDATA_PATH, "filmaffinity", "search_result_tile.html"),
            encoding="UTF-8",
        ) as result_tile:
            self.search_result_tile_list = [result_tile.read()]
        with open(
            os.path.join(TESTDATA_PATH, "filmaffinity", "movie_details_page.html"),
            encoding="UTF-8",
        ) as movie_details_page:
            self.movie_details_page = movie_details_page.read()

    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        FilmAffinityRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._on_search_result_page")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._is_requested_movie")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._get_search_results")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinity")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_insert(
        self,
        browser_mock,
        base_init_mock,
        site_mock,
        overview_page_mock,  # pylint: disable=too-many-arguments
        eq_check_mock,
        search_result_page_location,
        progress_print_mock,
    ):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        search_result_page_location.return_value = True
        inserter = FilmAffinityRatingsInserter(None)
        inserter.args = False
        inserter.site = site_mock
        inserter.site.site_name = "FilmAffinity"
        inserter.failed_movies = []

        inserter.insert([self.movie], Site.IMDB)

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._on_search_result_page")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinity")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success_by_year(self, browser_mock, base_init_mock, site_mock, search_result_page_location):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        search_result_page_location.return_value = True
        inserter = FilmAffinityRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "FilmAffinity"
        inserter.failed_movies = []

        movie2 = Movie(title="Ghost in the Shell", year=1995)

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._get_displayed_movie_year")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._on_movie_detail_page")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._on_search_result_page")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinity")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_directly(
        self,
        browser_mock,
        base_init_mock,
        site_mock,  # pylint: disable=too-many-arguments
        search_result_page_location,
        movie_detail_page_location,
        displayed_movie_year_mock,
    ):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.movie_details_page
        search_result_page_location.return_value = False
        movie_detail_page_location.return_value = True
        displayed_movie_year_mock.return_value = 1995
        inserter = FilmAffinityRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "FilmAffinity"
        inserter.failed_movies = []

        movie2 = Movie(title="Ghost in the Shell", year=1995)

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._is_requested_movie")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinityRatingsInserter._get_search_results")
    @patch("RatS.filmaffinity.filmaffinity_ratings_inserter.FilmAffinity")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_fail(
        self, browser_mock, base_init_mock, site_mock, tiles_mock, equality_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = FilmAffinityRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "FilmAffinity"
        inserter.failed_movies = []
        tiles_mock.return_value = self.search_result_tile_list
        equality_mock.return_value = False

        movie2 = Movie(title="The Matrix", year=1995)
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0137523", url="https://www.imdb.com/title/tt0137523", my_rating=9
        )

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)
