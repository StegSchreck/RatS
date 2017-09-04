import math

from RatS.base.base_ratings_parser import RatingsParser
from RatS.plex.plex_site import Plex
from RatS.utils.command_line import print_progress_bar


class PlexRatingsParser(RatingsParser):
    def __init__(self, args):
        super(PlexRatingsParser, self).__init__(Plex(args), args)
        self.processed_movies_count = 0

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        return math.ceil(float(movie_ratings_page.find('mediacontainer')['totalsize']) / 100)

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(movie_ratings_page.find('mediacontainer')['totalsize'])

    def _get_ratings_page(self, i):
        page_size = 100
        page_start = i * page_size
        return 'http://%s/library/sections/%s/all' \
               '?type=1&sort=rating:desc&X-Plex-Container-Start=%i&X-Plex-Container-Size=%i' \
               % (self.site.BASE_URL, self.site.MOVIE_SECTION_ID, page_start, page_size)

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find_all('video', attrs={'type': 'movie'})

    def _parse_movie_tile(self, movie_tile):
        movie = None

        if movie_tile.has_attr('userrating'):
            movie = dict()
            movie['title'] = movie_tile['title']
            movie['year'] = int(movie_tile['year'])
            movie[self.site.site_name.lower()] = dict()
            movie[self.site.site_name.lower()]['my_rating'] = round(float(movie_tile['userrating']))
            movie[self.site.site_name.lower()]['id'] = movie_tile['ratingkey']
            movie[self.site.site_name.lower()]['url'] = 'http://%s/web/index.html#!/server/%s/details/' % \
                                                        (self.site.BASE_URL, self.site.SERVER_ID) + \
                                                        '%2Flibrary%2Fmetadata%2F' + \
                                                        movie[self.site.site_name.lower()]['id']

        self.processed_movies_count += 1

        return movie

    def _print_progress_bar(self):
        print_progress_bar(self.processed_movies_count, self.movies_count, prefix=self.site.site_displayname)
