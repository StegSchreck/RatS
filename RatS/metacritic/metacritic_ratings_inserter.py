import time
import urllib.parse

from bs4 import BeautifulSoup

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.metacritic.metacritic_site import Metacritic
from RatS.utils import command_line


class MetacriticRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(MetacriticRatingsInserter, self).__init__(Metacritic(args), args)

    def _search_for_movie(self, movie):
        search_url = 'https://www.metacritic.com/search/movie/{movie_url_path}/results'.format(
            movie_url_path=urllib.parse.quote_plus(movie['title'])
        )
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', class_='result_wrap')

    def _is_requested_movie(self, movie, search_result):
        return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        movie_link = search_result.find(class_='product_title').find('a')
        self.site.browser.get('https://www.metacritic.com' + movie_link['href'])
        time.sleep(1)
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        page_title = movie_details_page.find(class_='product_page_title')
        if page_title:
            release_year = page_title.find(class_='release_year')
            if release_year and release_year.get_text():
                return movie['year'] == int(release_year.get_text())
        if self.args and self.args.verbose and self.args.verbose >= 3:
            command_line.info(
                '{movie_title} ({movie_year}): '
                'No release year displayed on {site_displayname} movie detail page {movie_detail_page} '
                '... skipping '.format(
                    site_displayname=self.site.site_name,
                    movie_title=movie['title'],
                    movie_year=movie['year'],
                    movie_detail_page=self.site.browser.current_url
                )
            )
        return False

    def _click_rating(self, my_rating):
        stars = self.site.browser.find_element_by_class_name('user_rating_widget').find_elements_by_class_name('ur')
        stars[my_rating].click()
