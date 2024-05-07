import logging
import re

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.base.movie_entity import Movie, SiteSpecificMovieData, Site
from RatS.movielens.movielens_site import Movielens


class MovielensRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(MovielensRatingsParser, self).__init__(Movielens(args), args)
        self.downloaded_file_name = "movielens-ratings.csv"

    def _call_download_url(self):
        self.site.browser.get("https://movielens.org/api/users/me/movielens-ratings.csv")

    def _convert_csv_row_to_movie(self, headers, row):
        if self.args and self.args.verbose and self.args.verbose >= 1:
            logging.info(f"===== {self.site.site_name}: reading movie from CSV: {[r for r in row]}")

        movie_year = self.__extract_year(row[headers.index("title")])
        movie = Movie(
            title=row[headers.index("title")].replace(str(movie_year), "").replace("()", "").strip(),
            year=movie_year,
        )

        movie_url_path = row[headers.index("movie_id")]
        movie.site_data[self.site.site] = SiteSpecificMovieData(
            id=row[headers.index("movie_id")],
            url=f"https://movielens.org/movies/{movie_url_path}",
            my_rating=int(float(row[headers.index("rating")]) * 2),
        )

        self.__extract_imdb_information(movie, row[headers.index("imdb_id")])
        self.__extract_tmdb_information(movie, row[headers.index("tmdb_id")])

        return movie

    @staticmethod
    def __extract_tmdb_information(movie: Movie, tmdb_id: str):
        movie.site_data[Site.TMDB] = SiteSpecificMovieData()
        movie.site_data[Site.TMDB].id = tmdb_id
        movie.site_data[Site.TMDB].url = f"https://www.themoviedb.org/movie/{movie.site_data[Site.TMDB].id}"

    @staticmethod
    def __extract_imdb_information(movie: Movie, imdb_id: str):
        if "tt" not in imdb_id:
            imdb_id = f"tt{imdb_id}"
        movie.site_data[Site.IMDB] = SiteSpecificMovieData(id=imdb_id, url=f"https://www.imdb.com/title/{imdb_id}")

    @staticmethod
    def __extract_year(title_field):
        find_year = re.findall(r"\((\d{4})\)", title_field)
        if find_year:
            return int(find_year[-1])
        # no movie year in CSV
        return 0
