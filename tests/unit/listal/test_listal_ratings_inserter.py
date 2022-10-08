import os
from unittest import TestCase
from unittest.mock import patch

from bs4 import BeautifulSoup

from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.listal.listal_ratings_inserter import ListalRatingsInserter

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class ListalRatingsInserterTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        self.movie = Movie(title="Fight Club", year=1999)
        self.movie.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0137523", url="https://www.imdb.com/title/tt0137523", my_rating=9
        )
        self.movie.site_data[Site.TMDB] = SiteSpecificMovieData(
            id="550",
            url="https://www.themoviedb.org/movie/550",
        )
        with open(
            os.path.join(TESTDATA_PATH, "listal", "search_result.html"),
            encoding="UTF-8",
        ) as search_results:
            self.search_results = search_results.read()
        with open(
            os.path.join(TESTDATA_PATH, "listal", "search_result_tile.html"),
            encoding="UTF-8",
        ) as result_tile:
            self.search_result_tile_list = [result_tile.read()]
        with open(
            os.path.join(TESTDATA_PATH, "listal", "movie_details_page.html"),
            encoding="UTF-8",
        ) as movie_details_page:
            self.movie_details_page = movie_details_page.read()

    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        ListalRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._post_movie_rating"
    )
    @patch("RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar")
    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._is_requested_movie"
    )
    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._get_search_results"
    )
    @patch("RatS.listal.listal_ratings_inserter.Listal")
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
        post_rating_mock,
    ):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = ListalRatingsInserter(None)
        inserter.args = False
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []

        inserter.insert([self.movie], Site.IMDB)

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_external_link_compare_imdb_fail(
        self, browser_mock, base_init_mock, site_mock
    ):
        site_mock.browser = browser_mock
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []

        result = inserter._compare_external_links(
            self.movie_details_page, self.movie, "imdb.com", Site.IMDB
        )  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_external_link_compare_imdb_success(
        self, browser_mock, base_init_mock, site_mock
    ):
        site_mock.browser = browser_mock
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []

        movie2 = Movie(title="The Simpsons", year=2007)
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0462538",
            url="https://www.imdb.com/title/tt0462538",
            my_rating=10,
        )

        result = inserter._compare_external_links(
            self.movie_details_page, movie2, "imdb.com", Site.IMDB
        )  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._compare_external_links"
    )
    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success_by_imdb(
        self, browser_mock, base_init_mock, site_mock, compare_mock
    ):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []
        compare_mock.return_value = True

        result = inserter._find_movie(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._is_requested_movie"
    )
    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._compare_external_links"
    )
    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success_by_year(
        self, browser_mock, base_init_mock, site_mock, compare_mock, equality_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []
        compare_mock.return_value = True
        equality_mock.return_value = True

        movie2 = Movie(title="Fight Club", year=1999)

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._is_requested_movie"
    )
    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._get_search_results"
    )
    @patch(
        "RatS.listal.listal_ratings_inserter.ListalRatingsInserter._compare_external_links"
    )
    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_fail(
        self,
        browser_mock,
        base_init_mock,
        site_mock,
        compare_mock,
        tiles_mock,
        equality_mock,
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_results
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []
        compare_mock.return_value = False
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

    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_compare_success_by_year(
        self, browser_mock, base_init_mock, site_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.movie_details_page
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []

        movie2 = Movie(title="Fight Club", year=1999)

        search_result = BeautifulSoup(self.search_result_tile_list[0], "html.parser")
        result = inserter._is_requested_movie(
            movie2, search_result
        )  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_compare_success_by_imdb(
        self, browser_mock, base_init_mock, site_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.movie_details_page
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []

        movie2 = Movie(title="Fight Club", year=1998)
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0137523",
            url="https://www.imdb.com/title/tt0137523",
            my_rating=9,
        )

        search_result = BeautifulSoup(self.search_result_tile_list[0], "html.parser")
        result = inserter._is_requested_movie(
            movie2, search_result
        )  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_compare_fail_by_year(
        self, browser_mock, base_init_mock, site_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.movie_details_page
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []

        movie2 = Movie(title="The Matrix", year=1995)

        search_result = BeautifulSoup(self.search_result_tile_list[0], "html.parser")
        result = inserter._is_requested_movie(
            movie2, search_result
        )  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch("RatS.listal.listal_ratings_inserter.Listal")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_target_movie_detail_page_has_no_year(
        self, browser_mock, base_init_mock, site_mock
    ):  # pylint: disable=too-many-arguments
        with open(
            os.path.join(
                TESTDATA_PATH, "listal", "movie_details_page_without_release_year.html"
            ),
            encoding="UTF-8",
        ) as movie_details_page_without_release_year:
            movie_details_page_without_release_year = (
                movie_details_page_without_release_year.read()
            )

        site_mock.browser = browser_mock
        browser_mock.page_source = movie_details_page_without_release_year
        inserter = ListalRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site_name = "Listal"
        inserter.failed_movies = []
        inserter.args = None

        movie2 = Movie(title="Fight Club", year=1999)

        search_result = BeautifulSoup(self.search_result_tile_list[0], "html.parser")
        result = inserter._is_requested_movie(
            movie2, search_result
        )  # pylint: disable=protected-access

        self.assertFalse(result)
