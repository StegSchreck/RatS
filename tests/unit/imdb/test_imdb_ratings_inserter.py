import os
from unittest import TestCase
from unittest.mock import patch

from bs4 import BeautifulSoup

from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.imdb.imdb_ratings_inserter import IMDBRatingsInserter

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)


class IMDBRatingsInserterTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, "exports")):
            os.makedirs(os.path.join(TESTDATA_PATH, "exports"))
        self.movie = Movie()
        self.movie.title = "Fight Club"
        self.movie.year = 1999
        self.movie.site_data[Site.IMDB] = SiteSpecificMovieData()
        self.movie.site_data[Site.IMDB].id = "tt0137523"
        self.movie.site_data[Site.IMDB].url = "https://www.imdb.com/title/tt0137523"
        self.movie.site_data[Site.TRAKT] = SiteSpecificMovieData()
        self.movie.site_data[Site.TRAKT].id = "432"
        self.movie.site_data[Site.TRAKT].url = "https://trakt.tv/movies/fight-club-1999"
        self.movie.site_data[Site.TRAKT].my_rating = "10"
        # self.movie.site_data[Site.TRAKT]["overall_rating"] = "89%"  # TODO
        self.movie.site_data[Site.TMDB] = SiteSpecificMovieData()
        self.movie.site_data[Site.TMDB].id = "550"
        self.movie.site_data[Site.TMDB].url = "https://www.themoviedb.org/movie/550"
        with open(
            os.path.join(TESTDATA_PATH, "imdb", "search_result.html"), encoding="UTF-8"
        ) as search_result_tile:
            self.search_result = search_result_tile.read()

    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        IMDBRatingsInserter(None)

        self.assertTrue(base_init_mock.called)

    @patch("RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar")
    @patch("RatS.imdb.imdb_ratings_inserter.IMDB")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_insert(
        self, browser_mock, base_init_mock, site_mock, progress_print_mock
    ):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        inserter = IMDBRatingsInserter(None)
        inserter.args = False
        inserter.site = site_mock
        inserter.site.site = Site.IMDB
        inserter.site.site_name = "IMDB"
        inserter.failed_movies = []

        inserter.insert([self.movie], Site.TRAKT)

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch("RatS.imdb.imdb_ratings_inserter.IMDB")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_is_requested_movie_success(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = IMDBRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site = Site.IMDB
        inserter.site.site_name = "IMDB"
        inserter.failed_movies = []
        search_result_page = BeautifulSoup(self.search_result, "html.parser")
        search_result = search_result_page.find(class_="findList").find_all(
            class_="findResult"
        )[0]

        result = inserter._is_requested_movie(
            self.movie, search_result
        )  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.imdb.imdb_ratings_inserter.IMDB")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_is_requested_movie_fail(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = IMDBRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site = Site.IMDB
        inserter.site.site_name = "IMDB"
        inserter.failed_movies = []
        search_result_page = BeautifulSoup(self.search_result, "html.parser")
        search_result = search_result_page.find(class_="findList").find_all(
            class_="findResult"
        )[0]

        movie2 = Movie()
        movie2.title = "Arrival"
        movie2.year = 2006

        result = inserter._is_requested_movie(
            movie2, search_result
        )  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch("RatS.imdb.imdb_ratings_inserter.IMDB")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_is_requested_movie_no_movie_with_that_year(
        self, browser_mock, base_init_mock, site_mock
    ):
        site_mock.browser = browser_mock
        inserter = IMDBRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site = Site.IMDB
        inserter.site.site_name = "IMDB"
        inserter.failed_movies = []
        search_result_page = BeautifulSoup(self.search_result, "html.parser")
        search_result = search_result_page.find(class_="findList").find_all(
            class_="findResult"
        )[0]

        movie2 = Movie()
        movie2.title = "SomeMovie"
        movie2.year = 1995

        result = inserter._is_requested_movie(
            movie2, search_result
        )  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch("RatS.imdb.imdb_ratings_inserter.IMDB")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_success(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_result
        inserter = IMDBRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site = Site.IMDB
        inserter.site.site_name = "IMDB"
        inserter.failed_movies = []

        result = inserter._find_movie(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch("RatS.imdb.imdb_ratings_inserter.IMDB")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_find_movie_fail(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_result
        inserter = IMDBRatingsInserter(None)
        inserter.site = site_mock
        inserter.site.site = Site.IMDB
        inserter.site.site_name = "IMDB"
        inserter.failed_movies = []

        movie2 = Movie()
        movie2.title = "The Matrix"
        movie2.year = 1995

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)
