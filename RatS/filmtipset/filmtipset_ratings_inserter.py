import math
import urllib.parse

from bs4 import BeautifulSoup

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Site, Movie
from RatS.filmtipset.filmtipset_site import Filmtipset
from RatS.imdb.imdb_site import IMDB


class FilmtipsetRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(FilmtipsetRatingsInserter, self).__init__(Filmtipset(args), args)

    def _search_for_movie(self, movie: Movie):
        search_params = urllib.parse.urlencode({"q": movie.title})
        search_url = f"https://www.filmtipset.se/hitta?{search_params}"
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        result_list = search_result_page.find("table", class_="list")
        if result_list:
            return result_list.find_all("tr")[1:]
        return list()

    def _is_requested_movie(self, movie: Movie, search_result):
        movie_year = search_result.find_all("td")[1].get_text()
        if int(movie_year) == int(movie.year):
            movie_url = search_result.find("a")["href"]
            self.site.browser.get(movie_url)
            return self._check_movie_details(movie)
        return False

    def _check_movie_details(self, movie: Movie):
        if Site.IMDB in movie.site_data:
            return self._compare_external_links(movie)
        return True

    def _compare_external_links(self, movie: Movie):
        try:
            movie_detail_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
            parsed_imdb_id = movie_detail_page.find_all("span", class_="postmeta")[3].find("a")["href"].split("/")[-1]
            normalized_parsed_imdb_id = IMDB.normalize_imdb_id(parsed_imdb_id)
            return normalized_parsed_imdb_id == IMDB.normalize_imdb_id(movie.site_data[Site.IMDB].id)
        except IndexError:
            return True

    def _post_movie_rating(self, my_rating: int):
        rating_to_insert = math.ceil(my_rating / 2)
        url_params = urllib.parse.urlencode({"vote": rating_to_insert})
        search_url = f"{self.site.browser.current_url}?{url_params}"
        self.site.browser.get(search_url)
