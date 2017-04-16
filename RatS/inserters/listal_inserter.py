import re
import sys
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.listal_site import Listal
from RatS.utils.command_line import print_progress


class ListalInserter(Inserter):
    def __init__(self):
        super(ListalInserter, self).__init__(Listal())

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['url'] != '':
                self.site.browser.get(movie[self.site.site_name.lower()]['url'])
                success = True
            else:
                success = self._find_movie(movie)
            if success:
                self._post_movie_rating(movie[source.lower()]['my_rating'])
            else:
                self.failed_movies.append(movie)
            counter += 1
            print_progress(counter, len(movies), prefix=self.site.site_name)

        self._print_summary(movies)
        self._handle_failed_movies(movies)
        self.site.kill_browser()

    def _find_movie(self, movie):
        self.site.browser.get('http://www.listal.com/search/movies/%s' % movie['title'])
        time.sleep(1)
        try:
            movie_tiles = self._get_movie_tiles(self.site.browser.page_source)
        except (NoSuchElementException, KeyError):
            time.sleep(3)
            movie_tiles = self._get_movie_tiles(self.site.browser.page_source)
        for tile in movie_tiles:
            if self._is_requested_movie(movie, tile):
                return True  # Found
        return False  # Not Found

    @staticmethod
    def _get_movie_tiles(overview_page):
        search_result_page = BeautifulSoup(overview_page, 'html.parser')
        return search_result_page.find_all('div', class_='itemcell')

    def _is_requested_movie(self, movie, tile):
        self.site.browser.get(tile.find('a')['href'])
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
