import os
from unittest import TestCase
from unittest.mock import patch

from RatS.moviepilot.moviepilot_ratings_parser import MoviePilotRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MoviePilotRatingsParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))
        with open(os.path.join(TESTDATA_PATH, 'moviepilot', 'my_ratings.html'), encoding='UTF-8') as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(os.path.join(TESTDATA_PATH, 'moviepilot', 'movie_details_page.html'),
                  encoding='UTF-8') as detail_page:
            self.detail_page = detail_page.read()

    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        MoviePilotRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.base.base_ratings_parser.RatingsParser._print_progress_bar')
    @patch('RatS.moviepilot.moviepilot_ratings_parser.MoviePilotRatingsParser._retrieve_pages_count_and_movies_count')
    @patch('RatS.moviepilot.moviepilot_ratings_parser.MoviePilotRatingsParser.parse_movie_details_page')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.moviepilot.moviepilot_ratings_parser.MoviePilot')
    def test_parser(self, site_mock, base_init_mock, browser_mock, parse_movie_mock, metrics_mock, progress_print_mock):  # pylint: disable=too-many-arguments
        browser_mock.page_source = self.my_ratings
        parser = MoviePilotRatingsParser(None)
        parser.args = False
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'MoviePilot'
        parser.site.browser = browser_mock
        parser.args = None
        parser.movies_count = 1
        metrics_mock.return_value = 1

        parser.parse()

        self.assertEqual(1, parse_movie_mock.call_count)
        self.assertEqual(1, len(parser.movies))
        self.assertEqual(dict, type(parser.movies[0]))
        self.assertEqual('Star Trek - Der Film', parser.movies[0]['title'])
        self.assertEqual('https://www.moviepilot.de/movies/star-trek-der-film', parser.movies[0]['moviepilot']['url'])

    @patch('RatS.moviepilot.moviepilot_ratings_parser.MoviePilotRatingsParser._get_movie_my_rating')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.moviepilot.moviepilot_ratings_parser.MoviePilot')
    def test_parser_single_movie(self, site_mock, base_init_mock, browser_mock, rating_mock):
        browser_mock.page_source = self.my_ratings
        parser = MoviePilotRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'MoviePilot'
        parser.site.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = dict()
        rating_mock.return_value = 10

        parser.parse_movie_details_page(movie)

        # Star Trek
        self.assertEqual(1979, movie['year'])
        self.assertEqual('1442', movie['moviepilot']['id'])
        self.assertEqual(10, movie['moviepilot']['my_rating'])
