import datetime
import os
import sys
import time

from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, \
    ElementNotInteractableException, TimeoutException

from RatS.utils import file_impex, command_line
from RatS.utils.command_line import print_progress_bar

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')


class RatingsInserter:
    def __init__(self, site, args):
        self.site = site
        self.args = args
        self.failed_movies = []
        self.exports_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
        if not os.path.exists(self.exports_folder):
            os.makedirs(self.exports_folder)
        self.failed_movies_filename = '{timestamp}_{site_name}_failed.json'.format(
            timestamp=TIMESTAMP,
            site_name=self.site.site_name
        )
        self.start_timestamp = time.time()

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write('\r===== {site_displayname}: posting {movies_count} movies                   \r\n'.format(
            site_displayname=self.site.site_displayname,
            movies_count=len(movies)
        ))
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

    def _is_field_in_parsed_data_for_this_site(self, movie, field):
        return self.site.site_name.lower() in movie and field in movie[self.site.site_name.lower()] and \
               movie[self.site.site_name.lower()][field] != ''

    def print_progress(self, counter, movie, movies):
        if self.args and self.args.verbose and self.args.verbose >= 2:
            sys.stdout.write('\r===== {site_displayname}: posted {movie} \r\n'.format(
                site_displayname=self.site.site_displayname,
                movie=movie
            ))
            sys.stdout.flush()
        elif self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write('\r===== {site_displayname}: posted {movie_title} ({movie_year})\r\n'.format(
                site_displayname=self.site.site_displayname,
                movie_title=movie['title'],
                movie_year=movie['year']
            ))
            sys.stdout.flush()
        else:
            self._print_progress_bar(counter, movies)

    def _print_progress_bar(self, counter, movies):
        print_progress_bar(
            iteration=counter,
            total=len(movies),
            start_timestamp=self.start_timestamp,
            prefix=self.site.site_displayname
        )

    def _go_to_movie_details_page(self, movie):
        if self._is_field_in_parsed_data_for_this_site(movie, 'url'):
            self.site.browser.get(movie[self.site.site_name.lower()]['url'])
            success = True
        else:
            success = self._find_movie(movie)
        return success

    def _find_movie(self, movie):
        try:
            self._search_for_movie(movie)
        except TimeoutException:
            return False
        time.sleep(1)

        iteration = 0
        search_results = None
        while not search_results:
            iteration += 1
            try:
                search_results = self._get_search_results(self.site.browser.page_source)
            except (NoSuchElementException, KeyError) as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue
            if iteration > 10:
                # log this?
                break

        return self._is_movie_in_search_results(movie, search_results)

    def _is_movie_in_search_results(self, movie, search_results):
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
        iteration = 0
        while True:
            iteration += 1
            try:
                self._click_rating(my_rating)
                break
            except (ElementNotVisibleException, NoSuchElementException, ElementNotInteractableException) as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

    def _click_rating(self, my_rating):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _print_summary(self, movies):
        success_number = len(movies) - len(self.failed_movies)
        sys.stdout.write('\r\n===== {site_displayname}: sucessfully posted {success_number}'
                         ' of {movies_count} movies\r\n'.format(
                             site_displayname=self.site.site_displayname,
                             success_number=success_number,
                             movies_count=len(movies)
                         ))
        sys.stdout.flush()

    def _handle_failed_movies(self, movies):
        if self.args and self.args.verbose and self.args.verbose >= 1:
            self._print_failed_movies()
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(movies, folder=self.exports_folder, filename=self.failed_movies_filename)
            sys.stdout.write('===== {site_displayname}: export data for {failed_number} failed movies to '
                             '{folder}/{filename}\r\n'.format(
                                 site_displayname=self.site.site_displayname,
                                 failed_number=len(self.failed_movies),
                                 folder=self.exports_folder,
                                 filename=self.failed_movies_filename
                             ))
        sys.stdout.flush()

    def _print_failed_movies(self):
        for failed_movie in self.failed_movies:
            sys.stdout.write('FAILED TO FIND: %s (%i)\r\n' % (failed_movie['title'], failed_movie['year']))
