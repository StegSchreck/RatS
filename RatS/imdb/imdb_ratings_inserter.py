import re
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.imdb.imdb_site import IMDB


class IMDBRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(IMDBRatingsInserter, self).__init__(IMDB(args), args)

    def _find_movie(self, movie):
        search_url = 'http://www.imdb.com/find?s=tt&ref_=fn_al_tt_mr&{search_params}'.format(
            search_params=urllib.parse.urlencode({'q': movie['title']})
        )
        self.site.browser.get(search_url)
        time.sleep(1)
        search_result_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        search_results_list = search_result_page.find(class_='findList')
        if search_results_list:  # found something
            search_results = search_results_list.find_all(class_='findResult')
            for search_result in search_results:
                if self._is_requested_movie(movie, search_result):
                    movie_url = "http://www.imdb.com" + search_result.find('a')['href']
                    self.site.browser.get(movie_url)
                    return True
            return False
        return False

    def _is_requested_movie(self, movie, search_result):
        result_annotation = search_result.find(class_='result_text').get_text()
        result_year_list = re.findall(r'\((\d{4})\)', result_annotation)
        if len(result_year_list) > 0:
            result_year = result_year_list[-1]
            return int(result_year) == movie['year']
        return False

    def _click_rating(self, my_rating):
        ratings_button = self.site.browser.find_element_by_class_name('star-rating-button')\
            .find_element_by_tag_name('button')
        stars = self.site.browser.find_element_by_class_name('star-rating-stars').find_elements_by_tag_name('a')
        star_index = int(my_rating) - 1
        builder = ActionChains(self.site.browser)
        builder.move_to_element(ratings_button).click(ratings_button)\
            .move_to_element(stars[star_index]).click(stars[star_index])\
            .perform()
        time.sleep(0.5)  # wait for POST request to be sent
