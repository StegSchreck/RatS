import sys
import time

from bs4 import BeautifulSoup

from RatS.utils.command_line import print_progress_bar


class RatingsParser:
    def __init__(self, site, args):
        self.site = site
        self.args = args

        self.movies = []
        self.movies_count = 0

        self.site.browser.get(self.site.MY_RATINGS_URL)

    def parse(self):
        try:
            self._parse_ratings()
        except AttributeError:
            time.sleep(2)  # wait a little bit for page to load and try again
            self._parse_ratings()
        self.site.kill_browser()
        return self.movies

    def _parse_ratings(self):
        movie_ratings_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        time.sleep(1)

        pages_count = self._get_pages_count(movie_ratings_page)
        self.movies_count = self._get_movies_count(movie_ratings_page)
        if self.args and self.args.verbose and self.args.verbose >= 3:
            sys.stdout.write('\r\n ================================================== \r\n')
            sys.stdout.write(self.site.browser.current_url)
            sys.stdout.write('\r\n ===== %s: getting page count: %i \r\n' %
                             (self.site.site_displayname, pages_count))
            sys.stdout.write('\r\n ===== %s: getting movies count: %i \r\n' %
                             (self.site.site_displayname, self.movies_count))
            # sys.stdout.write(str(self.site.browser.page_source))
            sys.stdout.write('\r\n ================================================== \r\n')
            sys.stdout.flush()

        sys.stdout.write('\r===== %s: Parsing %i pages with %i movies in total\r\n' %
                         (self.site.site_displayname, pages_count, self.movies_count))
        sys.stdout.flush()

        for i in range(1, pages_count + 1):
            self.site.browser.get(self._get_ratings_page(i))
            movie_listing_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            self._parse_movie_listing_page(movie_listing_page)

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _get_ratings_page(self, i):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_movie_listing_page(self, movie_listing_page):
        movies_tiles = self._get_movie_tiles(movie_listing_page)
        for movie_tile in movies_tiles:
            movie = self._parse_movie_tile(movie_tile)
            if movie:
                self.movies.append(movie)
            self.print_progress(movie)

    def print_progress(self, movie):
        if self.args and self.args.verbose and self.args.verbose >= 2:
            sys.stdout.write('\r===== %s: parsed %s \r\n' % (self.site.site_displayname, movie))
            sys.stdout.flush()
        elif self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write('\r===== %s: parsed %s (%i) \r\n' %
                             (self.site.site_displayname, movie['title'], movie['year']))
            sys.stdout.flush()
        else:
            self._print_progress_bar()

    def _print_progress_bar(self):
        print_progress_bar(len(self.movies), self.movies_count, prefix=self.site.site_displayname)

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_movie_tile(self, movie_tile):
        movie = dict()
        movie['title'] = self._get_movie_title(movie_tile)
        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['id'] = self._get_movie_id(movie_tile)
        movie[self.site.site_name.lower()]['url'] = self._get_movie_url(movie_tile)

        self.site.browser.get(movie[self.site.site_name.lower()]['url'])
        time.sleep(1)

        try:
            self.parse_movie_details_page(movie)
        except AttributeError:
            time.sleep(3)  # wait a little bit for page to load and try again
            self.parse_movie_details_page(movie)

        return movie

    @staticmethod
    def _get_movie_title(movie_tile):
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_movie_id(movie_tile):
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_movie_url(movie_tile):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def parse_movie_details_page(self, movie):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_external_links(self, movie, movie_details_page):
        external_links = self._get_external_links(movie_details_page)
        for link in external_links:
            if 'imdb.com' in link['href'] and 'find?' not in link['href']:
                movie['imdb'] = dict()
                movie['imdb']['url'] = link['href'].strip('/')
                movie['imdb']['id'] = movie['imdb']['url'].split('/')[-1]
            elif 'themoviedb.org' in link['href']:
                movie['tmdb'] = dict()
                movie['tmdb']['url'] = link['href'].strip('/')
                movie['tmdb']['id'] = movie['tmdb']['url'].split('/')[-1]

    @staticmethod
    def _get_external_links(movie_details_page):
        raise NotImplementedError("This is not the implementation you are looking for.")
