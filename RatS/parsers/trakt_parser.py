import time

import sys
from bs4 import BeautifulSoup

from RatS.data.movie import Movie
from RatS.parsers.base_parser import Parser
from RatS.sites.trakt import Trakt


class TraktRatingsParser(Parser):
    def __init__(self):
        super(TraktRatingsParser, self).__init__(Trakt())

    def parse(self):
        try:
            self._parse_ratings()
        except AttributeError:
            time.sleep(0.5)  # wait a little bit for page to load and try again
            self._parse_ratings()
        self.kill_browser()
        return self.movies

    def _parse_ratings(self):
        movie_ratings_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        pages_count = int(movie_ratings_page.find(id='rating-items').
                          find_all('li', class_='page')[-1].find('a').get_text())
        self.movies_count = int(movie_ratings_page.find('section', class_='subnav-wrapper').
                                find('a', attrs={'data-title': 'Movies'}).find('span').
                                get_text().strip().replace(',', ''))

        sys.stdout.write('===== Parsing %i pages with %i movies in total =====\r\n' % (pages_count, self.movies_count))
        sys.stdout.flush()
        # for i in range(1, 2):  # testing purpose
        for i in range(1, int(pages_count) + 1):
            self.browser.get(self.site.MY_RATINGS_URL + '?page=%i' % i)
            movie_listing_page = BeautifulSoup(self.browser.page_source, 'html.parser')
            self._parse_movie_listing_page(movie_listing_page)

    def _parse_movie_listing_page(self, movie_listing_page):
        movies_tiles = movie_listing_page.find(class_='row posters').find_all('div', attrs={'data-type': 'movie'})
        for movie_tile in movies_tiles:
            movie = self._parse_movie_tile(movie_tile)
            self.movies.append(movie)

    def _parse_movie_tile(self, movie_tile):
        movie = Movie()
        movie.trakt.id = movie_tile['data-movie-id']
        movie.trakt.url = 'https://trakt.tv%s' % movie_tile['data-url']
        movie.title = movie_tile.find('h3').get_text()
        movie.trakt.my_rating = movie_tile.find_all('h4')[1].get_text().strip()

        self.browser.get(movie.trakt.url)

        try:
            self.parse_movie_details_page(movie)
        except AttributeError:
            time.sleep(0.5)  # wait a little bit for page to load and try again
            self.parse_movie_details_page(movie)

        self.print_progress(len(self.movies), self.movies_count, bar_length=25, prefix="Progress:")

        return movie

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        movie.trakt.overall_rating = self._get_overall_rating(movie_details_page)
        self._parse_external_links(movie, movie_details_page)

    @staticmethod
    def _parse_external_links(movie, movie_page):
        external_links = movie_page.find(id='info-wrapper').find('ul', class_='external').find_all('a')
        for link in external_links:
            if 'imdb.com' in link['href']:
                movie.imdb.url = link['href']
                movie.imdb.id = movie.imdb.url.split('/')[-1]
            if 'themoviedb.org' in link['href']:
                movie.tmdb.url = link['href']
                movie.tmdb.id = movie.tmdb.url.split('/')[-1]

    @staticmethod
    def _get_overall_rating(movie_page):
        return movie_page.find(id='summary-ratings-wrapper').find('ul', class_='ratings') \
            .find('li', attrs={'itemprop': 'aggregateRating'}).find('div', class_='rating').get_text()
