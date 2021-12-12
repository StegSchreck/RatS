import re
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from RatS.allocine.allocine_site import AlloCine
from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Movie


class AlloCineRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(AlloCineRatingsInserter, self).__init__(AlloCine(args), args)

    def _search_for_movie(self, movie: Movie):
        search_params = urllib.parse.urlencode({"q": movie.title})
        search_url = f"https://www.allocine.fr/recherche/movie/?{search_params}"
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        return search_result_page.find_all("div", class_="entity-card")

    def _is_requested_movie(self, movie: Movie, search_result):
        if self._is_id_in_parsed_data_for_this_site(movie):
            return movie.site_data[self.site.site].id == search_result["data-movie-id"]
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie: Movie, search_result):
        try:
            movie_url = (
                "https://www.allocine.fr"
                + search_result.find("a", class_="thumbnail-link")["href"]
            )
        except KeyError:
            return False

        self.site.browser.get(movie_url)
        time.sleep(1)
        self.site.handle_privacy_notice_if_present()
        movie_details_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        release_date_element = movie_details_page.find(
            "div", class_="meta-body-info"
        ).find(class_="date")
        if release_date_element:
            release_date_text = release_date_element.get_text().strip()
            result_year_list = re.findall(r"(\d{4})", release_date_text)
            if len(result_year_list) > 0:
                result_year = result_year_list[-1]
                year_equal = int(result_year) == int(movie.year)
                return year_equal
        return False

    def _click_rating(self, my_rating: int):
        user_rating_section = self.site.browser.find_element(
            By.CLASS_NAME, "bam-container"
        )
        rating_stars = user_rating_section.find_elements(By.CLASS_NAME, "rating-star")
        stars_index = int(my_rating) - 1
        rating_stars[stars_index].click()
        time.sleep(1)
