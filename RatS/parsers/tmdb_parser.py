import sys
import time

from bs4 import BeautifulSoup

from RatS.parsers.base_parser import Parser
from RatS.sites.tmdb_site import TMDB
from RatS.utils.command_line import print_progress


class TMDBRatingsParser(Parser):
    def __init__(self):
        super(TMDBRatingsParser, self).__init__(TMDB())

    def parse(self):
        try:
            self._parse_ratings()
        except AttributeError:
            time.sleep(1)  # wait a little bit for page to load and try again
            self._parse_ratings()
        self.site.kill_browser()
        return self.movies

    def _parse_ratings(self):
        movie_ratings_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        pages_count = int(movie_ratings_page.find(class_='results').find(class_='pagination').
                          get_text().split(' ')[-3])
        self.movies_count = int(movie_ratings_page.find(class_='results').find(class_='pagination').find('span').
                                get_text().split(' ')[0].replace('(', ''))

        sys.stdout.write('\r===== %s: Parsing %i pages with %i movies in total\r\n' %
                         (self.site.site_name, pages_count, self.movies_count))
        sys.stdout.flush()

        for i in range(1, int(pages_count) + 1):
            self.site.browser.get(self.site.MY_RATINGS_URL + '?page=%i' % i)
            movie_listing_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            self._parse_movie_listing_page(movie_listing_page)

    def _parse_movie_listing_page(self, movie_listing_page):
        movies_tiles = movie_listing_page.find(class_='results').find_all('div', class_='item')
        for movie_tile in movies_tiles:
            movie = self._parse_movie_tile(movie_tile)
            self.movies.append(movie)

    def _parse_movie_tile(self, movie_tile):
        movie = dict()
        movie['title'] = movie_tile.find('p').find('a').get_text()
        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['id'] = movie_tile.find('p').find('a')['href'].split('/')[-1]
        movie[self.site.site_name.lower()]['url'] = 'https://www.themoviedb.org/movie/%s' % \
                                                    movie[self.site.site_name.lower()]['id']

        self.site.browser.get(movie[self.site.site_name.lower()]['url'])
        time.sleep(1)

        try:
            self.parse_movie_details_page(movie)
        except AttributeError:
            time.sleep(3)  # wait a little bit for page to load and try again
            self.parse_movie_details_page(movie)

        print_progress(len(self.movies), self.movies_count, prefix=self.site.site_name)

        return movie

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie['year'] = int(movie_details_page.find(class_='release_date').get_text().replace('(', '').replace(')', ''))
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['my_rating'] = \
            int(float(movie_details_page.find(id='rating_input')['value']) * 2)
