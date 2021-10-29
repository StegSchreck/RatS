import datetime
import os
import sys
import time

from progressbar import ProgressBar
from selenium.common.exceptions import (
    ElementNotVisibleException,
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
    WebDriverException,
)

from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")


class RatingsInserter:
    def __init__(self, site, args):
        self.site = site
        self.args = args

        self.failed_movies = []
        self.failed_movies_filename = f"{TIMESTAMP}_{self.site.site_name}_failed.json"

        self.exports_folder = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), os.pardir, os.pardir, "RatS", "exports"
            )
        )
        if not os.path.exists(self.exports_folder):
            os.makedirs(self.exports_folder)

        self.progress_bar = None

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write(
            f"\r===== {self.site.site_displayname}: posting {len(movies)} movies                     \r\n"
        )
        sys.stdout.flush()

        for movie in movies:
            movie_details_page_found = self._go_to_movie_details_page(movie)
            if movie_details_page_found:
                self._post_movie_rating(movie[source.lower()]["my_rating"])
            else:
                self.failed_movies.append(movie)
            counter += 1
            self.print_progress(counter, movie, movies)

        self._print_summary(movies)
        self._handle_failed_movies()
        self.site.browser_handler.kill()

    def _is_field_in_parsed_data_for_this_site(self, movie, field):
        return (
            self.site.site_name.lower() in movie
            and field in movie[self.site.site_name.lower()]
            and movie[self.site.site_name.lower()][field] != ""
        )

    def print_progress(self, counter, movie, movies):
        movie_index = movies.index(movie) + 1
        if self.args and self.args.verbose and self.args.verbose >= 2:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: [{movie_index}/{len(movies)}] posted {movie}\r\n"
            )
            sys.stdout.flush()
        elif self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: [{movie_index}/{len(movies)}] "
                f"posted {movie['title']} ({movie['year']})\r\n"
            )
            sys.stdout.flush()
        else:
            self._print_progress_bar(counter, movies)

    def _print_progress_bar(self, counter, movies):
        if not self.progress_bar:
            self.progress_bar = ProgressBar(max_value=len(movies), redirect_stdout=True)
        self.progress_bar.update(counter)
        if counter == len(movies):
            self.progress_bar.finish()

    def _go_to_movie_details_page(self, movie):
        if self._is_field_in_parsed_data_for_this_site(movie, "url"):
            self.site.open_url_with_521_retry(movie[self.site.site_name.lower()]["url"])
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
        while not search_results and iteration < 10:
            iteration += 1
            try:
                search_results = self._get_search_results(self.site.browser.page_source)
            except (NoSuchElementException, KeyError) as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

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
            except (
                ElementNotVisibleException,
                NoSuchElementException,
                ElementNotInteractableException,
                WebDriverException,
            ) as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

    def _click_rating(self, my_rating):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _print_summary(self, movies):
        success_number = len(movies) - len(self.failed_movies)
        sys.stdout.write(
            f"\r\n===== {self.site.site_displayname}: sucessfully posted {success_number}"
            f" of {len(movies)} movies\r\n"
        )
        sys.stdout.flush()

    def _handle_failed_movies(self):
        if self.args and self.args.verbose and self.args.verbose >= 1:
            self._print_failed_movies()
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(
                self.failed_movies,
                folder=self.exports_folder,
                filename=self.failed_movies_filename,
            )
            sys.stdout.write(
                f"===== {self.site.site_displayname}: export data for {len(self.failed_movies)}"
                f" failed movies to {self.exports_folder}/{self.failed_movies_filename}\r\n"
            )
        sys.stdout.flush()

    def _print_failed_movies(self):
        for failed_movie in self.failed_movies:
            sys.stdout.write(
                f"FAILED TO FIND: {failed_movie['title']} ({failed_movie['year']})\r\n"
            )
