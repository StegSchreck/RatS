from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.trakt.trakt_site import Trakt


class TraktRatingsParser(RatingsParser):
    def __init__(self, args):
        super(TraktRatingsParser, self).__init__(Trakt(args), args)

    def _get_ratings_page(self, i):
        return '%s?page=%i' % (self.site.MY_RATINGS_URL, i)

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(movie_ratings_page.find('section', class_='subnav-wrapper').
                   find('a', attrs={'data-title': 'Movies'}).find('span').
                   get_text().strip().replace(',', ''))

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        return int(movie_ratings_page.find(id='rating-items').
                   find_all('li', class_='page')[-1].find('a').get_text())

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find(class_='row posters').find_all('div', attrs={'data-type': 'movie'})

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find('h3').get_text()

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile['data-movie-id']

    @staticmethod
    def _get_movie_url(movie_tile):
        return 'https://trakt.tv%s' % movie_tile['data-url']

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie['year'] = int(movie_details_page.find(class_='year').get_text())
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['my_rating'] = self._get_movie_my_rating(movie_details_page)
        self._parse_external_links(movie, movie_details_page)

    @staticmethod
    def _get_movie_my_rating(movie_details_page):
        return int(movie_details_page.find('div', class_='rated-text').find('div', class_='rating').get_text())

    @staticmethod
    def _get_external_links(movie_details_page):
        return movie_details_page.find(id='info-wrapper').find('ul', class_='external').find_all('a')
