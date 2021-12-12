import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Movie, Site
from RatS.imdb.imdb_site import IMDB
from RatS.trakt.trakt_site import Trakt


class TraktRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(TraktRatingsInserter, self).__init__(Trakt(args), args)

    def _search_for_movie(self, movie: Movie):
        search_params = urllib.parse.urlencode({"query": movie.title})
        search_url = f"https://trakt.tv/search/?{search_params}"
        self.site.open_url_with_521_retry(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        return search_result_page.find_all("div", attrs={"data-type": "movie"})

    def _is_requested_movie(self, movie: Movie, search_result):
        if self._is_id_in_parsed_data_for_this_site(movie):
            return movie.site_data[self.site.site].id == search_result["data-movie-id"]
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie: Movie, search_result):
        try:
            movie_url = "https://trakt.tv" + search_result["data-url"]
        except KeyError:
            return False

        self.site.open_url_with_521_retry(movie_url)
        time.sleep(1)
        if Site.IMDB in movie.site_data and movie.site_data[Site.IMDB].id:
            return self._compare_external_links(
                self.site.browser.page_source, movie, "imdb.com", Site.IMDB
            )
        elif Site.TMDB in movie and movie.site_data[Site.TMDB].id != "":
            return self._compare_external_links(
                self.site.browser.page_source, movie, "themoviedb.org", Site.TMDB
            )
        else:
            movie_details_page = BeautifulSoup(
                self.site.browser.page_source, "html.parser"
            )
            year_str = movie_details_page.find(class_="year").get_text().strip()
            return year_str != "" and movie.year == int(year_str)

    @staticmethod
    def _compare_external_links(page_source, movie, external_url_base, site: Site):
        movie_details_page = BeautifulSoup(page_source, "html.parser")
        external_links = (
            movie_details_page.find(id="info-wrapper")
            .find("ul", class_="external")
            .find_all("a")
        )
        for link in external_links:
            if external_url_base in link["href"]:
                if site == Site.IMDB:
                    return IMDB.normalize_imdb_id(
                        movie.site_data[Site.IMDB].id
                    ) == IMDB.normalize_imdb_id(link["href"].split("/")[-1])
                return movie.site_data[site].id == link["href"].split("/")[-1]
        return False

    def _click_rating(self, my_rating: int):
        user_rating_section = self.site.browser.find_element(
            By.CLASS_NAME, "summary-user-rating"
        )
        user_rating = user_rating_section.find_element(
            By.CLASS_NAME, "number"
        ).find_elements(By.CLASS_NAME, "rating")
        if user_rating:
            current_rating = int(user_rating[0].text)
        else:
            current_rating = 0
        if current_rating is not my_rating:  # prevent un-rating if same score
            user_rating_section.click()
            time.sleep(1)
            star_index = 10 - int(my_rating)
            self.site.browser.execute_script(
                f"$('.rating-hearts').find('label')[{star_index}].click()"
            )
            time.sleep(1)
