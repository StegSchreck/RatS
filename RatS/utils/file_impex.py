import csv
import datetime
import json
import os
import sys
import time
import zipfile
from typing import List, Dict

from RatS.base.movie_entity import Movie, Site, SiteSpecificMovieData

EXPORTS_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "RatS", "exports")
)
CSV_HEADER = "Const,Your Rating,Date Rated,Title,URL,Title Type,IMDb Rating,Runtime (mins),Year,Genres,Num Votes,Release Date,Directors\n"  # pylint: disable=line-too-long


def default(obj):
    if hasattr(obj, "to_json"):
        return obj.to_json()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def load_movies_from_json(
    folder: str = EXPORTS_FOLDER, filename: str = "import.json"
) -> List[Movie]:
    with open(os.path.join(folder, filename), encoding="UTF-8") as input_file:
        load: Dict = json.loads(input_file.read())
        return [Movie.from_json(item) for item in load]


def save_movies_to_json(
    movies: List[Movie], folder: str = EXPORTS_FOLDER, filename: str = "export.json"
):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), "w+", encoding="UTF-8") as output_file:
        output_file.write(json.dumps(movies, default=default))


def wait_for_file_to_exist(filepath: str, seconds: int = 30):
    iteration = 0
    while iteration < seconds:
        iteration += 1
        try:
            with open(filepath, "rb") as file:
                return file
        except IOError:
            time.sleep(1)  # try every second
            continue
    raise IOError(f"Could not access {filepath} after {seconds} seconds")


def load_movies_from_csv(filepath: str, encoding: str = "UTF-8") -> List[Movie]:
    sys.stdout.write("===== getting movies from CSV\r\n")
    sys.stdout.flush()
    wait_for_file_to_exist(filepath)
    with open(filepath, newline="", encoding=encoding) as input_file:
        reader = csv.reader(input_file, delimiter=",")
        headers = next(reader, None)
        return [convert_csv_row_to_movie(headers, row) for row in reader]


def convert_csv_row_to_movie(headers, row) -> Movie:
    movie_year = row[headers.index("Year")]
    movie = Movie(
        title=row[headers.index("Title")],
        year=int(movie_year) if movie_year else 0,
    )
    movie.site_data[Site.IMDB] = SiteSpecificMovieData(
        id=row[headers.index("Const")],
        url=row[headers.index("URL")].replace("http://", "https://"),
        my_rating=int(row[headers.index("Your Rating")]),
    )
    return movie


def save_movies_to_csv(
    movies: List[Movie],
    folder: str = EXPORTS_FOLDER,
    filename: str = "export.csv",
    rating_source: Site = Site.IMDB,
):
    sys.stdout.write("===== saving movies to CSV\r\n")
    sys.stdout.flush()
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), "w+", encoding="UTF-8") as output_file:
        output_file.write(CSV_HEADER)
        for i in range(len(movies)):
            output_file.write(convert_movie_to_csv(movies, i, rating_source))


def convert_movie_to_csv(movies: List[Movie], index: int, rating_source: Site) -> str:
    imdb_id = (
        movies[index].site_data[Site.IMDB].id
        if Site.IMDB in movies[index].site_data
        else ""
    )
    imdb_url = (
        movies[index].site_data[Site.IMDB].url
        if Site.IMDB in movies[index].site_data
        else ""
    )
    movie_csv = (
        ""
        + ""
        + imdb_id
        + ","
        + ""
        + str(movies[index].site_data[rating_source].my_rating)
        + ","
        + ""
        + datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
        + ","
        + '"'
        + movies[index].title
        + '",'
        + ""
        + imdb_url
        + ","
        + "movie,"
        + ","
        + ","
        + ""
        + str(movies[index].year)
        + ","
        + ","
        + ","
        + ""
        + str(movies[index].year)
        + "-01-01,"
        + ""
        + "\n"
    )
    return movie_csv


def extract_file_from_archive(
    path_to_zip_file: str, filename_to_extract: str, directory_to_extract_to: str
):
    if not os.path.exists(directory_to_extract_to):
        os.makedirs(directory_to_extract_to)
    zip_ref = zipfile.ZipFile(path_to_zip_file, "r")
    zip_ref.extract(filename_to_extract, directory_to_extract_to)
    zip_ref.close()
    os.remove(path_to_zip_file)
