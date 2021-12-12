import os
from unittest import TestCase
from unittest.mock import patch
from shutil import copyfile

from RatS.base.movie_entity import Movie, SiteSpecificMovieData, Site
from RatS.filmtipset.filmtipset_ratings_parser import FilmtipsetRatingsParser

TESTDATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets")
)
EXPORT_PATH = os.path.join(TESTDATA_PATH, "exports")


class FilmtipetParserTest(TestCase):
    def setUp(self):
        if not os.path.exists(EXPORT_PATH):
            os.makedirs(EXPORT_PATH)

    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_init(self, browser_mock, base_init_mock):
        parser = FilmtipsetRatingsParser(None)
        self.assertTrue(base_init_mock.called)
        self.assertEqual(parser.csv_delimiter, ";")

    @patch(
        "RatS.filmtipset.filmtipset_ratings_parser.FilmtipsetRatingsParser._file_was_downloaded"
    )
    @patch(
        "RatS.filmtipset.filmtipset_ratings_parser.FilmtipsetRatingsParser._repair_csv_file"
    )
    @patch("RatS.base.base_ratings_downloader.RatingsDownloader._parse_movies_from_csv")
    @patch(
        "RatS.filmtipset.filmtipset_ratings_parser.FilmtipsetRatingsParser._rename_csv_file"
    )
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.filmtipset.filmtipset_ratings_parser.Filmtipset")
    def test_parser(
        self,
        site_mock,
        base_init_mock,
        browser_mock,
        rename_csv_mock,
        parse_csv_mock,
        repair_mock,  # pylint: disable=too-many-arguments
        file_was_downloaded_mock,
    ):
        parser = FilmtipsetRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site_name = "Filmtipset"
        parser.site.browser = browser_mock
        parser.exports_folder = EXPORT_PATH
        parser.downloaded_file_name = "my_ratings.csv"
        parser.csv_filename = "1234567890_filmtipset.csv"
        file_was_downloaded_mock.return_value = True

        parser.parse()

        self.assertEqual(1, file_was_downloaded_mock.call_count)
        self.assertEqual(1, rename_csv_mock.call_count)
        self.assertEqual(1, repair_mock.call_count)
        self.assertEqual(1, parse_csv_mock.call_count)

    @patch(
        "RatS.filmtipset.filmtipset_ratings_parser.FilmtipsetRatingsParser._repair_csv_row"
    )
    def test_repair_csv_file(self, line_mock):
        original_test_file = os.path.join(TESTDATA_PATH, "filmtipset", "my_ratings.csv")
        copied_file = original_test_file + ".cp"
        copyfile(original_test_file, copied_file)
        line_mock.return_value = "a line\n"
        FilmtipsetRatingsParser._repair_csv_file(
            copied_file
        )  # pylint: disable=protected-access
        self.assertEqual(8, line_mock.call_count)
        os.remove(copied_file)

    def test_repair_csv_row(self):
        tests = [
            (
                "2012-02-05,Between You and Me;-1;2\n",
                '2012-02-05;"Between You and Me";-1;2\n',
            ),
            (
                "2004-01-16,Mina jag &amp; Irene;183505;3\n",
                '2004-01-16;"Mina jag &amp; Irene";183505;3\n',
            ),
            (
                "2004-12-08,Basic Instinct - iskallt begär;103772;3\n",
                '2004-12-08;"Basic Instinct - iskallt begär";103772;3\n',
            ),
            (
                "2019-04-27,Black Metal Satanica;;2\n",
                '2019-04-27;"Black Metal Satanica";;2\n',
            ),
            (
                '2019-04-27,A movie with "qoute";1234;2\n',
                '2019-04-27;"A movie with ""qoute""";1234;2\n',
            ),
            (
                '2020-09-22;"The King of Staten Island";9686708;4\n',
                '2020-09-22;"The King of Staten Island";9686708;4\n',
            ),
        ]
        for test in tests:
            line, expected_line = test
            newline = FilmtipsetRatingsParser._repair_csv_row(
                line
            )  # pylint: disable=protected-access
            self.assertEqual(expected_line, newline)

    @patch(
        "RatS.filmtipset.filmtipset_ratings_parser.FilmtipsetRatingsParser._extract_imdb_information"
    )
    @patch("RatS.utils.browser_handler.Firefox")
    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.filmtipset.filmtipset_ratings_parser.Filmtipset")
    def test_convert_csv_row_to_movie(
        self, site_mock, base_init_mock, browser_mock, imdb_mock
    ):
        parser = FilmtipsetRatingsParser(None)
        parser.movies = []
        parser.site = site_mock
        parser.site.site = Site.FILMTIPSET
        parser.site.site_name = "Filmtipset"
        parser.site.browser = browser_mock

        expected_site_date = SiteSpecificMovieData()
        expected_site_date.my_rating = 10
        expected_movie = Movie()
        expected_movie.title = "Hunt for the Wilderpeople"
        expected_movie.site_data[Site.FILMTIPSET] = expected_site_date
        headers = ["VoteDate", "MovieTitle", "IMDB", "Score"]
        row = ["2020-10-10", "Hunt for the Wilderpeople", "4698684", "5"]
        movie = parser._convert_csv_row_to_movie(
            headers, row
        )  # pylint: disable=protected-access
        self.assertEqual(1, imdb_mock.call_count)
        self.assertEqual(movie, expected_movie)

    def test_extract_imdb_information(self):
        tests = [
            (
                "1234567",
                {
                    "id": "tt1234567",
                    "url": "https://www.imdb.com/title/tt1234567",
                }
            ),
            (
                "12345",
                {
                    "id": "tt0012345",
                    "url": "https://www.imdb.com/title/tt0012345",
                }
            ),
        ]
        for test in tests:
            movie = Movie()
            num, expected_movie_details = test
            FilmtipsetRatingsParser._extract_imdb_information(
                movie, num
            )  # pylint: disable=protected-access
            self.assertEqual(movie.site_data[Site.IMDB].id, expected_movie_details['id'])
            self.assertEqual(movie.site_data[Site.IMDB].url, expected_movie_details['url'])

    @patch("RatS.base.base_ratings_parser.RatingsParser.__init__")
    @patch("RatS.utils.browser_handler.Firefox")
    def test_file_was_downloaded(self, browser_mock, base_init_mock):
        expected_file = "ft_betyg_2015-10-21.csv"
        path = os.path.join(EXPORT_PATH, expected_file)

        parser = FilmtipsetRatingsParser(None)
        parser.exports_folder = EXPORT_PATH
        parser.downloaded_file_name = "init test"

        exists = parser._file_was_downloaded()
        self.assertFalse(exists)
        self.assertNotEqual(parser.downloaded_file_name, expected_file)

        open(path, mode="a").close()

        exists = parser._file_was_downloaded()
        self.assertEqual(parser.downloaded_file_name, expected_file)
        self.assertTrue(exists)

        os.remove(path)
