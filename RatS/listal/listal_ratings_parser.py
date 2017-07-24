import re

from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.listal.listal_site import Listal


class ListalRatingsParser(RatingsParser):
    def __init__(self, args):
        super(ListalRatingsParser, self).__init__(Listal(args), args)

    def _get_ratings_page(self, i):
        return 'http://%s.listal.com/movies/all/%i/?rating=1' % (self.site.USERNAME, i)

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(movie_ratings_page.find('h1', class_='headingminiph').
                   get_text().replace('Movies', '').strip())

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        return [int(s) for s in re.findall(r'\b\d+\b',
                                           movie_ratings_page.find(id='displaychange')
                                           .find('div', class_='pages').find_all('a')[-2].get_text())][0]

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find(id='collectionwrapper').find_all('div', class_='gridviewinner')

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find_all('div')[1].find('a').get_text()

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile.find(class_='add-to-list')['data-productid']

    @staticmethod
    def _get_movie_url(movie_tile):
        return movie_tile.find_all('div')[1].find('a')['href']

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        release_date = movie_details_page.find(id='rightstuff').get_text()
        release_year = re.findall(r'Release date\:\s\d+\s\w+\s(\d{4})', release_date)
        if not release_year:
            movie_title = movie_details_page.find('h1', class_='itemheadingmedium').get_text()
            release_year = re.findall(r'\((\d{4})\)', movie_title)
        movie['year'] = int(release_year[0])
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['my_rating'] = self._get_movie_my_rating(movie_details_page)
        self._parse_external_links(movie, movie_details_page)

    @staticmethod
    def _get_movie_my_rating(movie_details_page):
        return int(movie_details_page.find(class_='current-rating')['style']
                   .replace('width:', '').replace('%;', '')) / 10

    @staticmethod
    def _get_external_links(movie_details_page):
        return movie_details_page.find(class_='ratingstable').find_all('a')
