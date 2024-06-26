import datetime
import logging
import os
import time

from progressbar import ProgressBar
from selenium.common.exceptions import (
    ElementNotVisibleException,
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
    WebDriverException,
)

from RatS.base.base_site import BaseSite
from RatS.base.movie_entity import Movie, Site
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")


class RatingsInserter:
    def __init__(self, site: BaseSite, args):
        self.site: BaseSite = site
        self.args = args

        self.failed_movies: list[Movie] = []
        self.failed_movies_filename = f"{TIMESTAMP}_{self.site.site_name}_failed.json"

        self.exports_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "RatS", "exports")
        )
        if not os.path.exists(self.exports_folder):
            os.makedirs(self.exports_folder)

        self.progress_bar = None

    def insert(self, movies: list[Movie], source: Site):
        counter = 0
        logging.info(f"===== {self.site.site_name}: posting {len(movies)} movies")

        for movie in movies:
            movie_details_page_found = self._go_to_movie_details_page(movie)
            if movie_details_page_found:
                self._post_movie_rating(movie.site_data[source].my_rating)
            else:
                self.failed_movies.append(movie)
            counter += 1
            self.print_progress(counter, movie, movies)

        self._print_summary(movies)
        self._handle_failed_movies()
        self.site.browser_handler.kill()

    def _is_id_in_parsed_data_for_this_site(self, movie: Movie):
        return self.site.site in movie.site_data and movie.site_data[self.site.site].id != ""

    def _is_url_in_parsed_data_for_this_site(self, movie: Movie):
        return self.site.site in movie.site_data and movie.site_data[self.site.site].url != ""

    def print_progress(self, counter: int, movie: Movie, movies: list[Movie]):
        movie_index = movies.index(movie) + 1
        logging.debug(f"===== {self.site.site_name}: [{movie_index}/{len(movies)}] posted {movie.title} ({movie.year})")
        self._print_progress_bar(counter, movies)

    def _print_progress_bar(self, counter: int, movies: list[Movie]):
        if not self.progress_bar:
            self.progress_bar = ProgressBar(max_value=len(movies), redirect_stdout=True)
        self.progress_bar.update(counter)
        if counter == len(movies):
            self.progress_bar.finish()

    def _go_to_movie_details_page(self, movie: Movie):
        if self._is_url_in_parsed_data_for_this_site(movie):
            self.site.open_url_with_521_retry(movie.site_data[self.site.site].url)
            success = True
        else:
            success = self._find_movie(movie)
        return success

    def _find_movie(self, movie: Movie):
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

    def _is_movie_in_search_results(self, movie: Movie, search_results):
        for search_result in search_results:
            if self._is_requested_movie(movie, search_result):
                return True  # Found
        return False  # Not Found

    def _search_for_movie(self, movie: Movie):
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_search_results(search_result_page):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _is_requested_movie(self, movie: Movie, search_result):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _post_movie_rating(self, my_rating: int):
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

    def _click_rating(self, my_rating: int):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _print_summary(self, movies: list[Movie]):
        success_number = len(movies) - len(self.failed_movies)
        logging.info(f"===== {self.site.site_name}: successfully posted {success_number} of {len(movies)} movies")

    def _handle_failed_movies(self):
        self._print_failed_movies()
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(
                self.failed_movies,
                folder=self.exports_folder,
                filename=self.failed_movies_filename,
            )
            logging.info(
                f"===== {self.site.site_name}: export data for {len(self.failed_movies)}"
                f" failed movies to {self.exports_folder}/{self.failed_movies_filename}"
            )

    def _print_failed_movies(self):
        for failed_movie in self.failed_movies:
            logging.warning(f"FAILED TO FIND: {failed_movie.title} ({failed_movie.year})")
