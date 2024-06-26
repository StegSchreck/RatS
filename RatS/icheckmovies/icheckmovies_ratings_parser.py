import logging
import time

from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.movie_entity import Movie, SiteSpecificMovieData
from RatS.icheckmovies.icheckmovies_site import ICheckMovies


class ICheckMoviesRatingsParser(RatingsParser):
    def __init__(self, args):
        super(ICheckMoviesRatingsParser, self).__init__(ICheckMovies(args), args)

    def _parse_ratings(self):
        self._parse_movies_category(self.site.MY_RATINGS_URL_FAVORITED, "liked")
        liked_movies = list(self.movies)
        self.movies = []
        self.progress_bar = None
        self._parse_movies_category(self.site.MY_RATINGS_URL_DISLIKED, "disliked")
        self.movies = self.movies + liked_movies

    def _parse_movies_category(self, url, category):
        self.site.browser.get(url)
        movie_ratings_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        time.sleep(1)
        self.movies_count = self._get_movies_count(movie_ratings_page)
        logging.info(f"===== {self.site.site_name}: Parsing {self.movies_count} {category} movies")
        self._parse_movie_listing_page(movie_ratings_page)

    def _parse_movie_tile(self, movie_tile):
        movie = Movie(
            title=self._get_movie_title(movie_tile),
            year=int(movie_tile.find("span", class_="info").find("a").get_text()),
        )
        movie.site_data[self.site.site] = SiteSpecificMovieData(
            id=self._get_movie_id(movie_tile),
            url=self._get_movie_url(movie_tile),
            my_rating=self._get_movie_my_rating(movie_tile),
        )

        self._parse_external_links(movie, movie_tile)

        return movie

    def _get_movie_my_rating(self, movie_tile):
        if "Remove" in movie_tile.find("a", class_="optionMarkFavorite").get_text():
            return int(self.site.PARSE_LIKE_TRANSLATION)
        if "Remove" in movie_tile.find("a", class_="optionMarkNotLike").get_text():
            return int(self.site.PARSE_DISLIKE_TRANSLATION)
        raise Exception

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return len(movie_ratings_page.find_all("li", class_="listItem"))

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find_all("li", class_="listItem")

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find("h2").find("a").get_text()

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile["id"].split("-")[0].replace("m", "")

    @staticmethod
    def _get_movie_url(movie_tile):
        movie_url_path = movie_tile.find("h2").find("a")["href"]
        return f"https://www.icheckmovies.com{movie_url_path}"

    @staticmethod
    def _get_external_links(movie_tile):  # pylint: disable=arguments-differ
        return [movie_tile.find("a", class_="optionIMDB")]
