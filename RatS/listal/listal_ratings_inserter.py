import re
import time
import urllib.parse

from bs4 import BeautifulSoup

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.listal.listal_site import Listal


class ListalRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(ListalRatingsInserter, self).__init__(Listal(args), args)

    def _search_for_movie(self, movie):
        search_url = 'http://www.listal.com/search/movies/{movie_url_path}'.format(
            movie_url_path=urllib.parse.quote_plus(movie['title'])
        )
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', class_='itemcell')

    def _is_requested_movie(self, movie, search_result):
        self.site.browser.set_page_load_timeout(10)

        iteration = 0
        while True:
            try:
                self.site.browser.get(search_result.find('a')['href'])
                break
            except AttributeError as e:
                iteration += 1
                if iteration > 10:
                    raise e
                self.site.browser.refresh()
                time.sleep(iteration * 1)
                continue

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
        return False

    def _post_movie_rating(self, my_rating):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie_id = movie_details_page.find('a', class_='rateproduct')['data-productid']

        self.site.browser.execute_script("""
            $.post(
                'http://www.listal.com/rate-product',
                {{
                    rating: '{my_rating}',
                    productid: '{movie_id}',
                    area: 'movies',
                    starType: 'small-star'
                }},
                function(data, status) {{}}
            );
        """.format(my_rating=my_rating, movie_id=movie_id))

        time.sleep(1)
