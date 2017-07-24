import time

from bs4 import BeautifulSoup

from RatS.base.base_inserter import Inserter
from RatS.metacritic.metacritic_site import Metacritic


class MetacriticRatingsInserter(Inserter):
    def __init__(self, args):
        super(MetacriticRatingsInserter, self).__init__(Metacritic(args), args)

    def _search_for_movie(self, movie):
        self.site.browser.get('http://www.metacritic.com/search/movie/%s/results' % movie['title'])

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', class_='result_wrap')

    def _is_requested_movie(self, movie, search_result):
        return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        movie_link = search_result.find(class_='product_title').find('a')
        self.site.browser.get('http://www.metacritic.com' + movie_link['href'])
        time.sleep(1)
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        return movie['year'] == int(movie_details_page.find(class_='product_page_title')
                                    .find(class_='release_year').get_text())

    def _click_rating(self, my_rating):
        stars = self.site.browser.find_element_by_class_name('user_rating_widget').find_elements_by_class_name('ur')
        stars[my_rating].click()
