import sys
import time

from bs4 import BeautifulSoup

from RatS.parsers.base_parser import Parser
from RatS.sites.trakt_site import Trakt
from RatS.utils.command_line import print_progress


class TraktRatingsParser(Parser):
    def __init__(self):
        super(TraktRatingsParser, self).__init__(Trakt())

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
        pages_count = int(movie_ratings_page.find(id='rating-items').
                          find_all('li', class_='page')[-1].find('a').get_text())
        self.movies_count = int(movie_ratings_page.find('section', class_='subnav-wrapper').
                                find('a', attrs={'data-title': 'Movies'}).find('span').
                                get_text().strip().replace(',', ''))

        sys.stdout.write('\r===== %s: Parsing %i pages with %i movies in total\r\n' %
                         (type(self.site).__name__, pages_count, self.movies_count))
        sys.stdout.flush()

        for i in range(1, int(pages_count) + 1):
            self.site.browser.get(self.site.MY_RATINGS_URL + '?page=%i' % i)
            movie_listing_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            self._parse_movie_listing_page(movie_listing_page)

    def _parse_movie_listing_page(self, movie_listing_page):
        movies_tiles = movie_listing_page.find(class_='row posters').find_all('div', attrs={'data-type': 'movie'})
        for movie_tile in movies_tiles:
            movie = self._parse_movie_tile(movie_tile)
            self.movies.append(movie)

    def _parse_movie_tile(self, movie_tile):
        movie = dict()
        movie['title'] = movie_tile.find('h3').get_text()
        movie[self.site.site_name] = dict()
        movie[self.site.site_name]['id'] = movie_tile['data-movie-id']
        movie[self.site.site_name]['url'] = 'https://trakt.tv%s' % movie_tile['data-url']
        movie[self.site.site_name]['my_rating'] = int(movie_tile.find_all('h4')[1].get_text().strip())

        self.site.browser.get(movie[self.site.site_name]['url'])

        try:
            self.parse_movie_details_page(movie)
        except AttributeError:
            time.sleep(1)  # wait a little bit for page to load and try again
            self.parse_movie_details_page(movie)

        print_progress(len(self.movies), self.movies_count, prefix=self.site.site_name)

        return movie

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie['year'] = int(movie_details_page.find(class_='year').get_text())
        if self.site.site_name not in movie:
            movie[self.site.site_name] = dict()
        self._parse_external_links(movie, movie_details_page)

    @staticmethod
    def _parse_external_links(movie, movie_page):
        external_links = movie_page.find(id='info-wrapper').find('ul', class_='external').find_all('a')
        for link in external_links:
            if 'imdb.com' in link['href']:
                movie['imdb'] = dict()
                movie['imdb']['url'] = link['href']
                movie['imdb']['id'] = movie['imdb']['url'].split('/')[-1]
            if 'themoviedb.org' in link['href']:
                movie['tmdb'] = dict()
                movie['tmdb']['url'] = link['href']
                movie['tmdb']['id'] = movie['tmdb']['url'].split('/')[-1]
