import re
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.listal.listal_site import Listal
from RatS.utils import command_line


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
            iteration += 1
            try:
                self.site.browser.get(search_result.find('a')['href'])
                break
            except (TimeoutException, AttributeError) as e:
                if iteration > 10:
                    raise e
                self.site.browser.refresh()
                time.sleep(iteration * 1)
                continue

        time.sleep(1)
        if 'imdb' in movie and movie['imdb']['id'] != '':
            return self._compare_external_links(self.site.browser.page_source, movie, 'imdb.com', 'imdb')
        else:
            return self._check_movie_details(movie)

    def _check_movie_details(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie_annotation = movie_details_page.find('h1', class_='itemheadingmedium').get_text()
        release_year = re.findall(r'\((\d{4})\)', movie_annotation)
        if release_year:
            movie_year = int(release_year[-1])
            return movie['year'] == movie_year
        else:
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
