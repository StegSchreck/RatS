import os
from unittest import TestCase
from unittest.mock import patch

from RatS.data.movie import Movie
from RatS.parsers.trakt_parser import TraktRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class TraktParserTest(TestCase):

    def setUp(self):
        with open(os.path.join(TESTDATA_PATH, 'my_ratings_page', 'trakt.html'), encoding='utf8') as my_ratings:
            self.my_ratings = my_ratings.read()
        with open(os.path.join(TESTDATA_PATH, 'movie_detail_page', 'trakt.html'), encoding='utf8') as detail_page:
            self.detail_page = detail_page.read()

    @patch('RatS.parsers.trakt_parser.TraktRatingsParser._parse_movie_details_page')
    @patch('RatS.parsers.base_parser.PhantomJS')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.trakt_parser.Trakt')
    def test_parser(self, trakt_mock, base_init_mock, browser_mock, parse_movie_mock):
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser()
        parser.movies = []
        parser.site = trakt_mock
        parser.browser = browser_mock

        parser.parse()

        self.assertEqual(60, parse_movie_mock.call_count)
        self.assertEqual(60, len(parser.movies))
        self.assertEqual(Movie, type(parser.movies[0]))
        self.assertEqual('Arrival', parser.movies[0].title)
        self.assertEqual('210803', parser.movies[0].trakt.id)
        self.assertEqual('https://trakt.tv/movies/arrival-2016', parser.movies[0].trakt.url)
        self.assertEqual('7', parser.movies[0].trakt.my_rating)

    @patch('RatS.parsers.base_parser.PhantomJS')
    @patch('RatS.parsers.base_parser.Parser.__init__')
    @patch('RatS.parsers.trakt_parser.Trakt')
    def test_parser_single_movie(self, trakt_mock, base_init_mock, browser_mock):
        browser_mock.page_source = self.my_ratings
        parser = TraktRatingsParser()
        parser.movies = []
        parser.site = trakt_mock
        parser.browser = browser_mock
        browser_mock.page_source = self.detail_page
        movie = Movie()

        parser._parse_movie_details_page(movie)  # pylint: disable=W0212

        self.assertEqual('75%', movie.trakt.overall_rating)
        self.assertEqual('tt2543164', movie.imdb.id)
        self.assertEqual('http://www.imdb.com/title/tt2543164', movie.imdb.url)
        self.assertEqual('329865', movie.tmdb.id)
        self.assertEqual('https://www.themoviedb.org/movie/329865', movie.tmdb.url)
