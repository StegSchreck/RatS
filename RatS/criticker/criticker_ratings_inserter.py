import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.criticker.criticker_site import Criticker
from RatS.imdb.imdb_site import IMDB


class CritickerRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(CritickerRatingsInserter, self).__init__(Criticker(args), args)

    def _search_for_movie(self, movie):
        search_params = urllib.parse.urlencode({"search": movie["title"]})
        search_url = f"https://www.criticker.com/?{search_params}&type=films"
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        return search_result_page.find_all("div", class_="titlerow")

    def _is_requested_movie(self, movie, search_result):
        if self._is_field_in_parsed_data_for_this_site(movie, "id"):
            return (
                movie[self.site.site_name.lower()]["id"]
                == search_result.find(_class="psi_rateit").find("a")["titleid"]
            )
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        movie_url = search_result.find(class_="titlerow_name").find("a")["href"]
        self.site.browser.get(movie_url)
        time.sleep(1)
        if "imdb" in movie and movie["imdb"]["id"] != "":
            return self._compare_external_links(
                self.site.browser.page_source, movie, "imdb.com", "imdb"
            )
        else:
            movie_details_page = BeautifulSoup(
                self.site.browser.page_source, "html.parser"
            )
            year = movie_details_page.find("h1").find_all("span")[1].get_text()
            return movie["year"] == int(year)

    @staticmethod
    def _compare_external_links(page_source, movie, external_url_base, site_name):
        movie_details_page = BeautifulSoup(page_source, "html.parser")
        try:
            external_links = movie_details_page.find(id="fi_info_ext").find_all("a")
        except AttributeError:
            return False
        for link in external_links:
            if external_url_base in link["href"]:
                return IMDB.normalize_imdb_id(
                    movie[site_name]["id"]
                ) == IMDB.normalize_imdb_id(link["href"].rstrip("/").split("/")[-1])
        return False

    def _post_movie_rating(self, my_rating):
        converted_rating = str(my_rating * 10)
        try:
            score = self.site.browser.find_element_by_id(
                "fi_scoring_div"
            ).find_element_by_class_name("rating")
            if (
                score.is_displayed() and not score.text == converted_rating
            ):  # already rated
                self.site.browser.find_element_by_id("fi_editrating_link").click()
                self._insert_rating(converted_rating)
        except NoSuchElementException:  # not rated yet
            self._insert_rating(converted_rating)

    def _insert_rating(self, converted_rating):
        score_input = self.site.browser.find_element_by_xpath(
            "//*[@id='fi_scoring_div']//input"
        )
        score_input.clear()
        score_input.send_keys(str(converted_rating))
        self.site.browser.find_element_by_xpath(
            "//*[@id='fi_scoring_div']//button"
        ).click()
