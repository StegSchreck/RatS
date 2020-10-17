import os
from unittest import TestCase
from unittest.mock import patch

from RatS.movielens.movielens_ratings_parser import MovielensRatingsParser

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class MovielensParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(os.path.join(TESTDATA_PATH, 'exports')):
            os.makedirs(os.path.join(TESTDATA_PATH, 'exports'))

    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.utils.browser_handler.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        MovielensRatingsParser(None)

        self.assertTrue(base_init_mock.called)

    @patch('RatS.movielens.movielens_ratings_parser.MovielensRatingsParser._parse_movies_from_csv')
    @patch('RatS.movielens.movielens_ratings_parser.MovielensRatingsParser._rename_csv_file')
    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.movielens.movielens_ratings_parser.Movielens')
    def test_parser(self, site_mock, base_init_mock, browser_mock, rename_csv_mock, parse_csv_mock):  # pylint: disable=too-many-arguments
        parser = MovielensRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Movielens'
        parser.site.browser = browser_mock
        parser.exports_folder = os.path.abspath(os.path.join(TESTDATA_PATH, 'exports'))
        parser.csv_filename = '1234567890_movielens.csv'
        parser.downloaded_file_name = os.path.join(os.pardir, 'movielens', 'my_ratings.csv')

        parser.parse()

        self.assertEqual(1, rename_csv_mock.call_count)
        self.assertEqual(1, parse_csv_mock.call_count)

    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.movielens.movielens_ratings_parser.Movielens')
    def test_csv_rename(self, site_mock, base_init_mock, browser_mock):  # pylint: disable=too-many-arguments
        parser = MovielensRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Movielens'
        parser.site.browser = browser_mock
        parser.exports_folder = os.path.abspath(os.path.join(TESTDATA_PATH, 'exports'))
        parser.csv_filename = '1234567890_movielens.csv'
        parser.downloaded_file_name = os.path.join(os.pardir, 'movielens', 'my_ratings.csv')

        self.assertFalse(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', 'movielens-ratings.csv')))
        with open(os.path.join(TESTDATA_PATH, 'exports', 'movielens-ratings.csv'), 'w+'):
            self.assertTrue(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', 'movielens-ratings.csv')))
        self.assertFalse(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', parser.csv_filename)))

        parser._rename_csv_file('movielens-ratings.csv')  # pylint: disable=protected-access

        self.assertFalse(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', 'movielens-ratings.csv')))
        self.assertTrue(os.path.isfile(os.path.join(TESTDATA_PATH, 'exports', parser.csv_filename)))
        os.remove(os.path.join(TESTDATA_PATH, 'exports', parser.csv_filename))

    @patch('RatS.utils.browser_handler.Firefox')
    @patch('RatS.base.base_ratings_parser.RatingsParser.__init__')
    @patch('RatS.movielens.movielens_ratings_parser.Movielens')
    def test_parse_movies_from_csv(self, site_mock, base_init_mock, browser_mock):
        parser = MovielensRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = 'Movielens'
        parser.site.browser = browser_mock
        parser.exports_folder = os.path.abspath(os.path.join(TESTDATA_PATH, 'exports'))
        parser.csv_filename = '1234567890_movielens.csv'
        parser.downloaded_file_name = os.path.join(os.pardir, 'movielens', 'my_ratings.csv')
        parser.args = None

        movies = parser._parse_movies_from_csv(os.path.join(TESTDATA_PATH, 'movielens', 'my_ratings.csv'))  # pylint: disable=protected-access

        self.assertEqual(1063, len(movies))
        self.assertEqual(dict, type(movies[0]))

        self.assertEqual('Toy Story', movies[0]['title'])
        self.assertEqual(1995, movies[0]['year'])
        self.assertEqual('1', movies[0]['movielens']['id'])
        self.assertEqual('https://movielens.org/movies/1', movies[0]['movielens']['url'])
        self.assertEqual(8, movies[0]['movielens']['my_rating'])

        self.assertEqual('tt0114709', movies[0]['imdb']['id'])
        self.assertEqual('https://www.imdb.com/title/tt0114709', movies[0]['imdb']['url'])
        self.assertEqual('862', movies[0]['tmdb']['id'])
        self.assertEqual('https://www.themoviedb.org/movie/862', movies[0]['tmdb']['url'])
