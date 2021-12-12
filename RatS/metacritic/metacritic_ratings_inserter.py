import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Movie
from RatS.metacritic.metacritic_site import Metacritic
from RatS.utils import command_line


class MetacriticRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(MetacriticRatingsInserter, self).__init__(Metacritic(args), args)

    def _search_for_movie(self, movie: Movie):
        movie_url_path = urllib.parse.quote_plus(movie.title)
        search_url = f"https://www.metacritic.com/search/movie/{movie_url_path}/results"
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        return search_result_page.find_all("div", class_="result_wrap")

    def _is_requested_movie(self, movie: Movie, search_result):
        return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie: Movie, search_result):
        movie_link = search_result.find(class_="product_title").find("a")
        self.site.browser.get("https://www.metacritic.com" + movie_link["href"])
        time.sleep(1)
        movie_details_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        page_title = movie_details_page.find(class_="product_page_title")
        if page_title:
            release_year = page_title.find(class_="release_year")
            if release_year and release_year.get_text():
                return movie.year == int(release_year.get_text())
        if self.args and self.args.verbose and self.args.verbose >= 3:
            command_line.info(
                f"{movie.title} ({movie.year}): "
                f"No release year displayed on {self.site.site_name} movie detail page {self.site.browser.current_url} "
                "... skipping "
            )
        return False

    def _click_rating(self, my_rating: int):
        stars = self.site.browser.find_element(
            By.CLASS_NAME, "user_rating_widget"
        ).find_elements(By.CLASS_NAME, "ur")
        stars[my_rating].click()
