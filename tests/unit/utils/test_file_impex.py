import csv
import datetime
import json
import os
import time
from shutil import copyfile
from unittest import TestCase

from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets"))
TESTDATA_NEW_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "assets", TIMESTAMP))


class FileHandlerTest(TestCase):
    def setUp(self):
        self.movie = Movie(title="Fight Club", year=1999)
        self.movie.site_data[Site.IMDB] = SiteSpecificMovieData(
            id="tt0137523", url="https://www.imdb.com/title/tt0137523", my_rating=10
        )
        self.movie.site_data[Site.TRAKT] = SiteSpecificMovieData(
            id="432", url="https://trakt.tv/movies/fight-club-1999", my_rating=10
        )
        self.movie.site_data[Site.TMDB] = SiteSpecificMovieData(id="550", url="https://www.themoviedb.org/movie/550")

    def test_load_movies_from_json(self):
        movies: list[Movie] = file_impex.load_movies_from_json(
            folder=os.path.join(TESTDATA_PATH, "trakt"),
            filename="exports.json",
        )
        self.assertEqual(1, len(movies))
        self.assertEqual(list, type(movies))
        self.assertEqual(Movie, type(movies[0]))
        self.assertEqual("Fight Club", movies[0].title)
        self.assertEqual(1999, movies[0].year)

        self.assertEqual(SiteSpecificMovieData, type(movies[0].site_data.get(Site.IMDB)))
        self.assertEqual("tt0137523", movies[0].site_data.get(Site.IMDB).id)
        self.assertEqual(
            "https://www.imdb.com/title/tt0137523/",
            movies[0].site_data.get(Site.IMDB).url,
        )
        self.assertEqual(10, movies[0].site_data.get(Site.IMDB).my_rating)

        self.assertEqual(SiteSpecificMovieData, type(movies[0].site_data.get(Site.TRAKT)))
        self.assertEqual("432", movies[0].site_data.get(Site.TRAKT).id)
        self.assertEqual(
            "https://trakt.tv/movies/fight-club-1999",
            movies[0].site_data.get(Site.TRAKT).url,
        )
        self.assertEqual(10, movies[0].site_data.get(Site.TRAKT).my_rating)

    def test_save_empty_movies_to_json(self):
        movies = []
        filename = os.path.join(os.path.join(TESTDATA_PATH, "exports"), "TEST_empty_movies.json")
        file_impex.save_movies_to_json(movies, os.path.join(TESTDATA_PATH, "exports"), "TEST_empty_movies.json")
        with open(filename) as file:
            self.assertEqual(movies, json.load(file))
        os.remove(filename)

    def test_save_empty_movies_to_json_in_new_folder(self):
        movies = []
        filename = os.path.join(TESTDATA_NEW_PATH, "TEST_empty_movies.json")
        file_impex.save_movies_to_json(movies, TESTDATA_NEW_PATH, "TEST_empty_movies.json")
        with open(filename) as file:
            self.assertEqual(movies, json.load(file))
        os.remove(filename)
        os.removedirs(TESTDATA_NEW_PATH)

    def test_save_single_movie_to_json(self):
        movies: list[Movie] = [self.movie]
        filename = os.path.join(os.path.join(TESTDATA_PATH, "exports"), "TEST_single_movie.json")
        file_impex.save_movies_to_json(movies, os.path.join(TESTDATA_PATH, "exports"), "TEST_single_movie.json")
        with open(filename) as file:
            json_from_file = json.load(file)
            self.assertEqual(1, len(json_from_file))
            self.assertDictEqual(self.movie.to_json(), json_from_file[0])
        os.remove(filename)

    def test_save_multiple_movies_to_json(self):
        movie2 = Movie(title="The Matrix", year=1999)
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData(id="tt0133093", url="https://www.imdb.com/title/tt0133093")
        movie2.site_data[Site.TRAKT] = SiteSpecificMovieData(
            id="481", url="https://trakt.tv/movies/the-matrix-1999", my_rating=9
        )

        movies: list[Movie] = [self.movie, movie2]
        filename = os.path.join(os.path.join(TESTDATA_PATH, "exports"), "TEST_multiple_movies.json")
        file_impex.save_movies_to_json(movies, os.path.join(TESTDATA_PATH, "exports"), "TEST_multiple_movies.json")
        with open(filename) as file:
            json_from_file = json.load(file)
            self.assertEqual(2, len(json_from_file))
            self.assertDictEqual(movies[0].to_json(), json_from_file[0])
            self.assertDictEqual(movies[1].to_json(), json_from_file[1])
        os.remove(filename)

    def test_load_movies_from_csv(self):
        parsed_movies = file_impex.load_movies_from_csv(os.path.join(TESTDATA_PATH, "imdb", "my_ratings.csv"))

        self.assertEqual(2, len(parsed_movies))
        self.assertEqual(Movie, type(parsed_movies[0]))
        self.assertEqual("Arrival", parsed_movies[0].title)
        self.assertEqual(2016, parsed_movies[0].year)
        self.assertEqual("tt2543164", parsed_movies[0].site_data[Site.IMDB].id)
        self.assertEqual(
            "https://www.imdb.com/title/tt2543164/",
            parsed_movies[0].site_data[Site.IMDB].url,
        )
        self.assertEqual(7, parsed_movies[0].site_data[Site.IMDB].my_rating)

    def test_save_single_movie_to_csv(self):
        movies = [self.movie]
        filename = os.path.join(os.path.join(TESTDATA_PATH, "exports"), "TEST_single_movie.csv")
        file_impex.save_movies_to_csv(
            movies,
            os.path.join(TESTDATA_PATH, "exports"),
            "TEST_single_movie.csv",
            Site.IMDB,
        )
        with open(filename) as file:
            reader = csv.reader(file, delimiter=",")
            headers = next(reader)
            row = next(reader)
            self.assertEqual(self.movie.title, row[headers.index("Title")])
            self.assertEqual(self.movie.year, int(row[headers.index("Year")]))
            self.assertEqual(self.movie.site_data[Site.IMDB].id, row[headers.index("Const")])
            self.assertEqual(self.movie.site_data[Site.IMDB].url, row[headers.index("URL")])
            self.assertEqual(
                self.movie.site_data[Site.IMDB].my_rating,
                int(row[headers.index("Your Rating")]),
            )
        os.remove(filename)

    def test_save_multiple_movies_to_csv(self):
        movie2 = Movie(title="Star Trek - Der Film", year=1979)
        movie2.site_data[Site.IMDB] = SiteSpecificMovieData(id="tt0079945", url="https://www.imdb.com/title/tt0079945")
        movie2.site_data[Site.TRAKT] = SiteSpecificMovieData(
            id="117",
            url="https://trakt.tv/movies/star-trek-the-motion-picture-1979",
            my_rating=8,
        )

        movies = [self.movie, movie2]
        filename = os.path.join(os.path.join(TESTDATA_PATH, "exports"), "TEST_multiple_movies.csv")
        file_impex.save_movies_to_csv(
            movies,
            os.path.join(TESTDATA_PATH, "exports"),
            "TEST_multiple_movies.csv",
            Site.TRAKT,
        )
        with open(filename) as file:
            reader = csv.reader(file, delimiter=",")
            headers = next(reader)  # csv header
            row1 = next(reader)
            self.assertEqual(self.movie.title, row1[headers.index("Title")])
            self.assertEqual(self.movie.year, int(row1[headers.index("Year")]))
            self.assertEqual(self.movie.site_data[Site.IMDB].id, row1[headers.index("Const")])
            self.assertEqual(self.movie.site_data[Site.IMDB].url, row1[headers.index("URL")])
            self.assertEqual(
                self.movie.site_data[Site.TRAKT].my_rating,
                int(row1[headers.index("Your Rating")]),
            )
            row2 = next(reader)
            self.assertEqual(movie2.title, row2[headers.index("Title")])
            self.assertEqual(movie2.year, int(row2[headers.index("Year")]))
            self.assertEqual(movie2.site_data[Site.IMDB].id, row2[headers.index("Const")])
            self.assertEqual(movie2.site_data[Site.IMDB].url, row2[headers.index("URL")])
            self.assertEqual(
                movie2.site_data[Site.TRAKT].my_rating,
                int(row2[headers.index("Your Rating")]),
            )
        os.remove(filename)

    def test_extract_file_from_archive(self):
        os.makedirs(TESTDATA_NEW_PATH)
        test_zip_archive = os.path.join(TESTDATA_NEW_PATH, "letterboxd.zip")
        copyfile(
            os.path.join(TESTDATA_PATH, "letterboxd", "my_ratings.zip"),
            test_zip_archive,
        )
        extracted_file = os.path.join(TESTDATA_NEW_PATH, "ratings.csv")

        self.assertTrue(os.path.isfile(test_zip_archive))
        self.assertFalse(os.path.isfile(extracted_file))

        file_impex.extract_file_from_archive(test_zip_archive, "ratings.csv", TESTDATA_NEW_PATH)

        self.assertFalse(os.path.isfile(test_zip_archive))
        self.assertTrue(os.path.isfile(extracted_file))

        os.remove(extracted_file)
        os.removedirs(TESTDATA_NEW_PATH)
