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
        search_url = 'http://{base_url}/library/all?type=1&title={movie_title}' \
                     '&X-Plex-Container-Start=0' \
                     '&X-Plex-Container-Size=50' \
                     '&X-Plex-Token={plex_token}'.format(
                         base_url=self.site.BASE_URL,
                         movie_title=urllib.request.quote(movie['title']),
                         plex_token=self.site.PLEX_TOKEN
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
            movie_url = 'http://{base_url}/web/index.html#!/server/{server_id}/details' \
                        '?key={library_path}{movie_id}'.format(
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
        movie_id = self.site.browser.current_url.split('%2Flibrary%2Fmetadata%2F')[-1]
        rate_url = 'http://{base_url}/:/rate' \
                   '?key={movie_id}&identifier=com.plexapp.plugins.library' \
                   '&rating={my_rating}&X-Plex-Token={plex_token}'.format(
                       base_url=self.site.BASE_URL,
                       movie_id=movie_id,
                       my_rating=my_rating,
                       plex_token=self.site.PLEX_TOKEN
                   )
        self.site.browser.get(rate_url)
