import datetime
import os
import sys
import time

from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, \
    ElementNotInteractableException

from RatS.utils import file_impex
from RatS.utils.command_line import print_progress_bar

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class RatingsInserter:
    def __init__(self, site, args):
        self.site = site
        self.args = args
        self.failed_movies = []
        self.exports_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
        self.failed_movies_filename = '%s_%s_failed.json' % (TIMESTAMP, self.site.site_name)

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_displayname, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            movie_details_page_found = self._go_to_movie_details_page(movie)
            if movie_details_page_found:
                self._post_movie_rating(movie[source.lower()]['my_rating'])
            else:
                self.failed_movies.append(movie)
            counter += 1
            self.print_progress(counter, movie, movies)

        self._print_summary(movies)
        self._handle_failed_movies(movies)
        self.site.kill_browser()

    def print_progress(self, counter, movie, movies):
        if self.args.verbose and self.args.verbose >= 2:
            sys.stdout.write('\r===== %s: posted %s \r\n' % (self.site.site_displayname, movie))
            sys.stdout.flush()
        elif self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write('\r===== %s: posted %s (%i)\r\n' %
                             (self.site.site_displayname, movie['title'], movie['year']))
            sys.stdout.flush()
        else:
            print_progress_bar(counter, len(movies), prefix=self.site.site_displayname)

    def _go_to_movie_details_page(self, movie):
        if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['url'] != '':
            self.site.browser.get(movie[self.site.site_name.lower()]['url'])
            success = True
        else:
            success = self._find_movie(movie)
        return success

    def _find_movie(self, movie):
        self._search_for_movie(movie)
        time.sleep(1)
        try:
            search_results = self._get_search_results(self.site.browser.page_source)
        except (NoSuchElementException, KeyError):
            time.sleep(3)
            search_results = self._get_search_results(self.site.browser.page_source)
        for search_result in search_results:
            if self._is_requested_movie(movie, search_result):
                return True  # Found
        return False  # Not Found

    def _search_for_movie(self, movie):
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_search_results(search_result_page):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _is_requested_movie(self, movie, search_result):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _post_movie_rating(self, my_rating):
        try:
            self._click_rating(my_rating)
        except (ElementNotVisibleException, NoSuchElementException, ElementNotInteractableException):
            time.sleep(3)
            self._click_rating(my_rating)

    def _click_rating(self, my_rating):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _print_summary(self, movies):
        success_number = len(movies) - len(self.failed_movies)
        sys.stdout.write('\r\n===== %s: sucessfully posted %i of %i movies\r\n' %
                         (self.site.site_displayname, success_number, len(movies)))
        sys.stdout.flush()

    def _handle_failed_movies(self, movies):
        for failed_movie in self.failed_movies:
            sys.stdout.write('FAILED TO FIND: %s (%i)\r\n' % (failed_movie['title'], failed_movie['year']))
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(movies, folder=self.exports_folder, filename=self.failed_movies_filename)
            sys.stdout.write('===== %s: export data for %i failed movies to %s/%s\r\n' %
                             (self.site.site_displayname, len(self.failed_movies),
                              self.exports_folder, self.failed_movies_filename))
        sys.stdout.flush()
