import sys
import time

import re
from bs4 import BeautifulSoup

from RatS.parsers.base_parser import Parser
from RatS.sites.listal_site import Listal
from RatS.utils.command_line import print_progress


class ListalRatingsParser(Parser):
    def __init__(self):
        super(ListalRatingsParser, self).__init__(Listal())

    def _parse_ratings(self):
        movie_ratings_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')

        pages_count = [int(s) for s in re.findall(r'\b\d+\b',
                       movie_ratings_page.find(id='displaychange')
                       .find('div', class_='pages').find_all('a')[-2].get_text())][0]
        self.movies_count = int(movie_ratings_page.find('h1', class_='headingminiph').
                                get_text().replace('Movies', '').strip())

        sys.stdout.write('\r===== %s: Parsing %i pages with %i movies in total\r\n' %
                         (self.site.site_name, pages_count, self.movies_count))
        sys.stdout.flush()

        for i in range(1, pages_count + 1):
            url = 'http://%s.listal.com/movies/all/%i/?rating=1' % (self.site.USERNAME, i)
            self.site.browser.get(url)
            movie_listing_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            self._parse_movie_listing_page(movie_listing_page)

    def _parse_movie_listing_page(self, movie_listing_page):
        movies_tiles = movie_listing_page.find(id='collectionwrapper').find_all('div', class_='gridviewinner')
        for movie_tile in movies_tiles:
            movie = self._parse_movie_tile(movie_tile)
            self.movies.append(movie)

    def _parse_movie_tile(self, movie_tile):
        movie = dict()
        tile_header = movie_tile.find_all('div')[1]
        movie['title'] = tile_header.find('a').get_text()
        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['id'] = movie_tile.find(class_='add-to-list')['data-productid']
        movie[self.site.site_name.lower()]['url'] = tile_header.find('a')['href']
        percentage = movie_tile.find(id='rating').find(class_='current-rating')['style']\
            .replace('width:', '').replace('%;', '')
        movie[self.site.site_name.lower()]['my_rating'] = int(percentage) / 10

        self.site.browser.get(movie[self.site.site_name.lower()]['url'])

        try:
            self.parse_movie_details_page(movie)
        except AttributeError:
            time.sleep(1)  # wait a little bit for page to load and try again
            self.parse_movie_details_page(movie)

        print_progress(len(self.movies), self.movies_count, prefix=self.site.site_name)

        return movie

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        release_date = movie_details_page.find(id='rightstuff').get_text()
        movie['year'] = int(re.findall(r'Release date\:\s\d+\s\w+\s(\d{4})', release_date)[0])
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        self._parse_external_links(movie, movie_details_page)

    @staticmethod
    def _parse_external_links(movie, movie_details_page):
        external_links = movie_details_page.find(class_='ratingstable').find_all('a')
        for link in external_links:
            if 'imdb.com' in link['href']:
                movie['imdb'] = dict()
                movie['imdb']['url'] = link['href'].strip('/')
                movie['imdb']['id'] = movie['imdb']['url'].split('/')[-1]
