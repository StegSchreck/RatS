import re
import sys

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.movielens.movielens_site import Movielens


class MovielensRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(MovielensRatingsParser, self).__init__(Movielens(args), args)
        self.downloaded_file_name = "movielens-ratings.csv"

    def _call_download_url(self):
        self.site.browser.get(
            "https://movielens.org/api/users/me/movielens-ratings.csv"
        )

    def _convert_csv_row_to_movie(self, headers, row):
        movie = Movie()

        if self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: reading movie from CSV: \r\n"
            )
            for r in row:
                sys.stdout.write(r + "\r\n")
            sys.stdout.flush()

        year = self.__extract_year(movie, row[headers.index("title")])
        movie.title = row[headers.index("title")].replace(year, "").strip()

        movie.site_data[self.site.site] = SiteSpecificMovieData()
        movie.site_data[self.site.site].id = row[headers.index("movie_id")]
        movie_url_path = row[headers.index("movie_id")]
        movie.site_data[self.site.site][
            "url"
        ] = f"https://movielens.org/movies/{movie_url_path}"
        movie.site_data[self.site.site].my_rating = int(
            float(row[headers.index("rating")]) * 2
        )

        self.__extract_imdb_information(movie, row[headers.index("imdb_id")])
        self.__extract_tmdb_information(movie, row[headers.index("tmdb_id")])

        return movie

    @staticmethod
    def __extract_tmdb_information(movie, tmdb_id):
        movie["tmdb"] = SiteSpecificMovieData()
        movie["tmdb"]["id"] = tmdb_id
        movie["tmdb"]["url"] = f"https://www.themoviedb.org/movie/{movie['tmdb']['id']}"

    @staticmethod
    def __extract_imdb_information(movie, imdb_id):
        movie.site_data[Site.IMDB] = SiteSpecificMovieData()
        movie.site_data[Site.IMDB].id = imdb_id
        if "tt" not in movie.site_data[Site.IMDB].id:
            movie.site_data[Site.IMDB].id = f"tt{imdb_id}"
        movie.site_data[Site.IMDB][
            "url"
        ] = f"https://www.imdb.com/title/{movie['imdb']['id']}"

    @staticmethod
    def __extract_year(movie, title_field):
        find_year = re.findall(r"(\(\d{4}\))", title_field)
        if find_year:
            year = find_year[-1]
            movie.year = int(re.findall(r"\((\d{4})\)", title_field)[-1])
        else:  # no movie year in CSV
            year = "()"
            movie.year = 0
        return year
