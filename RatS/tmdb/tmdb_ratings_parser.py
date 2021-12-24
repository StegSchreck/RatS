import math

from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.movie_entity import SiteSpecificMovieData, Movie
from RatS.tmdb.tmdb_site import TMDB


class TMDBRatingsParser(RatingsParser):
    def __init__(self, args):
        super(TMDBRatingsParser, self).__init__(TMDB(args), args)

    def _get_ratings_page(self, page_number: int):
        return f"{self.site.MY_RATINGS_URL}?page={page_number}"

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(
            movie_ratings_page.find("div", class_="title_header")
            .find("a", attrs={"data-media-type": "movie"})
            .find("span")
            .get_text()
            .replace(".", "")
            .replace(",", "")
        )

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        movies_count = int(
            movie_ratings_page.find("div", class_="title_header")
            .find("a", attrs={"data-media-type": "movie"})
            .find("span")
            .get_text()
            .replace(".", "")
            .replace(",", "")
        )
        return math.ceil(movies_count / 50.0)

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find(class_="results_page").find_all(
            "div", class_="card"
        )

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find(class_="title").find("a").find("h2").get_text()

    def _parse_movie_tile(self, movie_tile):
        movie = Movie(
            title=self._get_movie_title(movie_tile),
            year=self._get_movie_year(movie_tile),
        )
        movie.site_data[self.site.site] = SiteSpecificMovieData(
            id=self._get_movie_id(movie_tile),
            url=self._get_movie_url(movie_tile),
            my_rating=self._get_movie_my_rating(movie_tile),
        )

        return movie

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile.find(class_="title").find("a")["href"].split("/")[-1]

    @staticmethod
    def _get_movie_url(movie_tile):
        return (
            "https://www.themoviedb.org"
            + movie_tile.find(class_="title").find("a")["href"]
        )

    @staticmethod
    def _get_movie_my_rating(movie_tile):
        return int(movie_tile.find(class_="account_rating").get_text())

    @staticmethod
    def _get_movie_year(movie_tile):
        release_date = movie_tile.find(class_="release_date")
        if release_date:
            return int(release_date.get_text().split(" ")[-1])
        else:
            return 0
