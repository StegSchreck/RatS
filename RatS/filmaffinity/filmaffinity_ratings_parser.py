import re

from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.filmaffinity.filmaffinity_site import FilmAffinity


class FilmAffinityRatingsParser(RatingsParser):
    def __init__(self, args):
        super(FilmAffinityRatingsParser, self).__init__(FilmAffinity(args), args)

    def _get_ratings_page(self, page_number):
        return f"{self.site.MY_RATINGS_URL}?p={page_number}"

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(movie_ratings_page.find('div', class_='user-ratings-list').
                   find('div', class_='count').find('b').get_text().strip().replace(',', ''))

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        # pages_count = int(movie_ratings_page.find('div', class_='user-ratings-list').
        #                    find('div', class_='count').find('b').get_text().strip().replace(',', ''))
        # return math.ceil(pages_count / 20.0)
        ratings_section = movie_ratings_page.find('div', class_='user-ratings-list')
        if ratings_section:
            pagination_section = ratings_section.find('div', class_='pager').find('div', class_='pager')
            if pagination_section:
                return int(pagination_section.find_all('a')[-2].get_text())
        return 1

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find_all('div', class_='user-ratings-movie')

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find(class_='mc-title').find('a').get_text().strip()

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile.find(class_='movie-card')['data-movie-id']

    @staticmethod
    def _get_movie_url(movie_tile):
        return movie_tile.find(class_='mc-title').find('a')['href']

    def _go_to_movie_details_page(self, movie):
        # all necessary information is displayed on the search results page
        # so there is no need to go to the movie details page
        pass

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie['year'] = self._get_movie_year(movie_details_page, movie[self.site.site_name.lower()]['id'])
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['my_rating'] = \
            self._get_movie_my_rating(movie_details_page, movie[self.site.site_name.lower()]['id'])

    @staticmethod
    def _get_movie_year(movie_details_page, movie_id):
        movie_tile = movie_details_page.find('div', attrs={'data-movie-id': movie_id}).parent.parent
        release_year = re.findall(r'\((\d{4})\)', movie_tile.find(class_='mc-title').get_text())
        if release_year:
            return int(release_year[0])
        else:
            return 0

    @staticmethod
    def _get_movie_my_rating(movie_details_page, movie_id):
        movie_tile = movie_details_page.find('div', attrs={'data-movie-id': movie_id}).parent.parent
        my_rating = int(movie_tile.find('div', class_='rate-wrapper').find('span', class_='avg-rat-wrapper').get_text())
        return my_rating
