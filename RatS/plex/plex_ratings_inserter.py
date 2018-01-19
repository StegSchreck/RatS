import math
import urllib.request

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
from selenium.webdriver.support.wait import WebDriverWait

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.plex.plex_site import Plex


class PlexRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(PlexRatingsInserter, self).__init__(Plex(args), args)

    def _search_for_movie(self, movie):
        search_url = 'http://{base_url}/search?local=1&query={search_params}'.format(
            base_url=self.site.BASE_URL, search_params=urllib.request.quote(movie['title'])
        )

        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        search_results = search_result_page.find_all('video', attrs={'type': 'movie'})
        return search_results

    def _is_requested_movie(self, movie, search_result):
        is_requested_movie = False

        if search_result.has_attr('year'):  # some movies might not have a year in Plex
            is_requested_movie = movie['year'] == int(search_result['year'])

        if is_requested_movie:
            movie_id = search_result['ratingkey']
            movie_url = 'http://{base_url}/web/index.html#!/server/{server_id}/details/{library_path}{movie_id}'.format(
                base_url=self.site.BASE_URL,
                server_id=self.site.SERVER_ID,
                library_path='%2Flibrary%2Fmetadata%2F',
                movie_id=movie_id
            )
            self.site.browser.get(movie_url)
            self._wait_for_movie_page_to_be_loaded()
            return True

        return False

    def _wait_for_movie_page_to_be_loaded(self):
        wait = ui.WebDriverWait(self.site.browser, 120)
        wait.until(lambda driver: driver.find_element_by_class_name('loading'))
        WebDriverWait(self.site.browser, 120).until(
            expected_conditions.invisibility_of_element_located((By.CLASS_NAME, 'loading'))
        )

    def _click_rating(self, my_rating):
        stars = self.site.browser.find_element_by_class_name('rating').find_elements_by_css_selector('span.star')
        star_index = math.ceil(int(my_rating) / 2) - 1
        stars[star_index].click()
