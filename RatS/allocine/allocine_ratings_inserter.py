import re
import time
import urllib.parse

from bs4 import BeautifulSoup

from RatS.allocine.allocine_site import AlloCine
from RatS.base.base_ratings_inserter import RatingsInserter


class AlloCineRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(AlloCineRatingsInserter, self).__init__(AlloCine(args), args)

    def _search_for_movie(self, movie):
        search_url = 'http://www.allocine.fr/recherche/movie/?{search_params}'.format(
            search_params=urllib.parse.urlencode({'q': movie['title']})
        )
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', class_='entity-card')

    def _is_requested_movie(self, movie, search_result):
        if self._is_field_in_parsed_data_for_this_site(movie, 'id'):
            return movie[self.site.site_name.lower()]['id'] == search_result['data-movie-id']
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        try:
            movie_url = 'http://www.allocine.fr' + search_result.find('a', class_='thumbnail-link')['href']
        except KeyError:
            return False

        self.site.browser.get(movie_url)
        time.sleep(1)
        self.site.handle_privacy_notice_if_present()
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        release_date_element = movie_details_page.find('div', class_='meta-body-info').find(class_='date')
        if release_date_element:
            release_date_text = release_date_element.get_text().strip()
            result_year_list = re.findall(r'(\d{4})', release_date_text)
            if len(result_year_list) > 0:
                result_year = result_year_list[-1]
                year_equal = int(result_year) == int(movie['year'])
                return year_equal
        return False

    def _click_rating(self, my_rating):
        user_rating_section = self.site.browser.find_element_by_class_name('bam-container')
        rating_stars = user_rating_section.find_elements_by_class_name('rating-star')
        stars_index = int(my_rating) - 1
        rating_stars[stars_index].click()
        time.sleep(1)
