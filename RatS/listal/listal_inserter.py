import re
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

from RatS.base.base_inserter import Inserter
from RatS.listal.listal_site import Listal


class ListalRatingsInserter(Inserter):
    def __init__(self, args):
        super(ListalRatingsInserter, self).__init__(Listal(args), args)

    def _search_for_movie(self, movie):
        self.site.browser.get('http://www.listal.com/search/movies/%s' % movie['title'])

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', class_='itemcell')

    def _is_requested_movie(self, movie, search_result):
        self.site.browser.set_page_load_timeout(10)
        try:
            self.site.browser.get(search_result.find('a')['href'])
        except TimeoutException:
            self.site.browser.refresh()
            time.sleep(2)
            self.site.browser.get(search_result.find('a')['href'])
        time.sleep(1)
        if 'imdb' in movie and movie['imdb']['id'] != '':
            return self._compare_external_links(self.site.browser.page_source, movie, 'imdb.com', 'imdb')
        else:
            movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            movie_annotation = movie_details_page.find('h1', class_='itemheadingmedium').get_text()
            movie_year = int(re.findall(r'\((\d{4})\)', movie_annotation)[-1])
            return movie['year'] == movie_year

    @staticmethod
    def _compare_external_links(page_source, movie, external_url_base, site_name):
        movie_details_page = BeautifulSoup(page_source, 'html.parser')
        external_links = movie_details_page.find(class_='ratingstable').find_all('a')
        for link in external_links:
            if external_url_base in link['href']:
                link_href = link['href'].strip('/')
                return movie[site_name]['id'] == link_href.split('/')[-1]

    def _post_movie_rating(self, my_rating):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie_id = movie_details_page.find('a', class_='rateproduct')['data-productid']

        self.site.browser.execute_script("""
            $.post(
                'http://www.listal.com/rate-product',
                {
                    rating: '%s',
                    productid: '%s',
                    area: 'movies',
                    starType: 'small-star'
                },
                function(data, status) {}
            );
        """ % (my_rating, movie_id))

        time.sleep(1)
