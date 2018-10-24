import math

from progressbar import ProgressBar

from RatS.base.base_ratings_parser import RatingsParser
from RatS.plex.plex_site import Plex


class PlexRatingsParser(RatingsParser):
    def __init__(self, args):
        super(PlexRatingsParser, self).__init__(Plex(args), args)
        self.processed_movies_count = 0
        self.standard_progress_bar = None

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        return math.ceil(float(movie_ratings_page.find('mediacontainer')['totalsize']) / 100)

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(movie_ratings_page.find('mediacontainer')['totalsize'])

    def _get_ratings_page(self, i):
        page_size = 100
        page_start = i * page_size
        return 'http://{base_url}/library/sections/{section_id}/all' \
               '?type=1&sort=rating:desc&X-Plex-Container-Start={page_start}&X-Plex-Container-Size={page_size}'.format(
                   base_url=self.site.BASE_URL,
                   section_id=self.site.MOVIE_SECTION_ID,
                   page_start=page_start,
                   page_size=page_size
               )

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
            movie[self.site.site_name.lower()]['url'] = \
                'http://{base_url}/web/index.html#!/server/{server_id}/details/{library_path}{movie_id}'.format(
                    base_url=self.site.BASE_URL,
                    server_id=self.site.SERVER_ID,
                    library_path='%2Flibrary%2Fmetadata%2F',
                    movie_id=movie[self.site.site_name.lower()]['id']
            )

        self.processed_movies_count += 1

        return movie

    def _print_progress_bar(self):
        if not self.standard_progress_bar:
            self.standard_progress_bar = ProgressBar(
                max_value=self.movies_count, redirect_stdout=True)
        self.standard_progress_bar.update(self.processed_movies_count)
        if self.movies_count == self.processed_movies_count:
            self.standard_progress_bar.finish()
