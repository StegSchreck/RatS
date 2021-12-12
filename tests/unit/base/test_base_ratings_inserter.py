from unittest import TestCase
from unittest.mock import patch

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Site, SiteSpecificMovieData, Movie


class BaseInserterTest(TestCase):
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock):
        with patch("RatS.base.base_site.Site") as site_mock:
            inserter = RatingsInserter(site_mock, None)

            self.assertEqual(inserter.site, site_mock)

    @patch("RatS.utils.file_impex.save_movies_to_json")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter._click_rating")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter._go_to_movie_details_page")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_one_failed_movie_to_be_printed(
        self,
        browser_mock,
        search_success_mock,
        click_rating_mock,  # pylint: disable=too-many-arguments
        progress_bar_mock,
        save_movies_to_json_mock,
    ):
        with patch("RatS.base.base_site.Site") as site_mock:
            inserter = RatingsInserter(site_mock, None)

        movie = Movie()
        movie.title = "Fight Club"
        movie.year = 1999
        movie.site_data[Site.IMDB] = SiteSpecificMovieData()
        movie.site_data[Site.IMDB].id = "tt0137523"
        movie.site_data[Site.IMDB].url = "https://www.imdb.com/title/tt0137523"
        movie.site_data[Site.IMDB].my_rating = 9

        movie2 = Movie()
        movie2.title = "unreadable movie"
        movie2.year = 1111
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData()
        movie2.site_data[Site.IMDB].id = "xxx"
        movie2.site_data[Site.IMDB].url = "https://www.imdb.com/title/xxx"
        movie2.site_data[Site.IMDB].my_rating = 4

        movies = [movie, movie, movie2]
        search_success_mock.side_effect = [True, True, False]

        inserter.insert(movies, Site.IMDB)

        self.assertEqual(1, len(inserter.failed_movies))
        save_movies_to_json_mock.assert_called_with(
            [movie2],
            folder=inserter.exports_folder,
            filename=inserter.failed_movies_filename,
        )

    @patch("RatS.utils.file_impex.save_movies_to_json")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter._print_progress_bar")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter._click_rating")
    @patch("RatS.base.base_ratings_inserter.RatingsInserter._go_to_movie_details_page")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_two_failed_movies_to_be_printed(
        self,
        browser_mock,
        search_success_mock,
        click_rating_mock,  # pylint: disable=too-many-arguments
        progress_bar_mock,
        save_movies_to_json_mock,
    ):
        with patch("RatS.base.base_site.Site") as site_mock:
            inserter = RatingsInserter(site_mock, None)

        movie = Movie()
        movie.title = "Fight Club"
        movie.year = 1999
        movie.site_data[Site.IMDB] = SiteSpecificMovieData()
        movie.site_data[Site.IMDB].id = "tt0137523"
        movie.site_data[Site.IMDB].url = "https://www.imdb.com/title/tt0137523"
        movie.site_data[Site.IMDB].my_rating = 9

        movie2 = Movie()
        movie2.title = "unreadable movie"
        movie2.year = 1111
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData()
        movie2.site_data[Site.IMDB].id = "xxx"
        movie2.site_data[Site.IMDB].url = "https://www.imdb.com/title/xxx"
        movie2.site_data[Site.IMDB].my_rating = 4

        movies = [movie, movie2, movie2]
        search_success_mock.side_effect = [True, False, False]

        inserter.insert(movies, Site.IMDB)

        self.assertEqual(2, len(inserter.failed_movies))
        save_movies_to_json_mock.assert_called_with(
            [movie2, movie2],
            folder=inserter.exports_folder,
            filename=inserter.failed_movies_filename,
        )
