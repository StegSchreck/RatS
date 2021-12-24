import os
import sys
import time
from typing import List

from bs4 import BeautifulSoup
from progressbar import ProgressBar

from RatS.base.base_site import BaseSite
from RatS.base.movie_entity import Movie, SiteSpecificMovieData, Site


class RatingsParser:
    def __init__(self, site: BaseSite, args):
        self.site: BaseSite = site
        self.args = args
        if not self.site.CREDENTIALS_VALID:
            return

        self.movies: List[Movie] = []
        self.movies_count: int = 0

        self.site.open_url_with_521_retry(self.site.MY_RATINGS_URL)

        self.exports_folder: str = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), os.pardir, os.pardir, "RatS", "exports"
            )
        )
        if not os.path.exists(self.exports_folder):
            os.makedirs(self.exports_folder)

        self.progress_bar = None

    def parse(self):
        iteration = 0
        while True:
            iteration += 1
            try:
                self._parse_ratings()
                break
            except AttributeError as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 2)
                continue

        self.site.browser_handler.kill()
        return self.movies

    def _parse_ratings(self):
        movie_ratings_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        time.sleep(1)

        pages_count: int = self._retrieve_pages_count_and_movies_count(
            movie_ratings_page
        )
        if self.args and self.args.verbose and self.args.verbose >= 3:
            sys.stdout.write(
                "\r\n ================================================== \r\n"
            )
            sys.stdout.write(self.site.browser.current_url)
            sys.stdout.write(
                f"\r\n ===== {self.site.site_displayname}: getting page count: {pages_count} \r\n"
            )
            sys.stdout.write(
                f"\r\n ===== {self.site.site_displayname}: getting movies count: {self.movies_count} \r\n"
            )
            sys.stdout.write(
                "\r\n ================================================== \r\n"
            )
            sys.stdout.flush()

        sys.stdout.write(
            f"\r===== {self.site.site_displayname}: Parsing {pages_count} pages"
            f" with {self.movies_count} movies in total\r\n"
        )
        sys.stdout.flush()

        for page_number in range(1, pages_count + 1):
            self.site.open_url_with_521_retry(self._get_ratings_page(1))
            movie_listing_page = BeautifulSoup(
                self.site.browser.page_source, "html.parser"
            )
            self._parse_movie_listing_page(movie_listing_page)

    def _retrieve_pages_count_and_movies_count(self, movie_ratings_page) -> int:
        pages_count = self._get_pages_count(movie_ratings_page)
        self.movies_count = self._get_movies_count(movie_ratings_page)
        return pages_count

    @staticmethod
    def _get_pages_count(movie_ratings_page) -> int:
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_movies_count(movie_ratings_page) -> int:
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _get_ratings_page(self, page_number: int):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_movie_listing_page(self, movie_listing_page):
        movies_tiles = self._get_movie_tiles(movie_listing_page)
        for movie_tile in movies_tiles:
            movie = self._parse_movie_tile(movie_tile)
            if movie:
                self.movies.append(movie)
            self.print_progress(movie)

    def print_progress(self, movie: Movie):
        if self.args and self.args.verbose and self.args.verbose >= 2:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: [{len(self.movies)}/{self.movies_count}] parsed {movie} \r\n"
            )
            sys.stdout.flush()
        elif self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write(
                f"\r===== {self.site.site_displayname}: [{len(self.movies)}/{self.movies_count}]"
                f" parsed {movie.title} ({movie.year}) \r\n"
            )
            sys.stdout.flush()
        else:
            self._print_progress_bar()

    def _print_progress_bar(self):
        if not self.progress_bar:
            self.progress_bar = ProgressBar(
                max_value=self.movies_count, redirect_stdout=True
            )
        self.progress_bar.update(len(self.movies))
        if self.movies_count == len(self.movies):
            self.progress_bar.finish()

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_movie_tile(self, movie_tile):
        movie = Movie(title=self._get_movie_title(movie_tile))
        movie_id = self._get_movie_id(movie_tile)
        site_specific_movie_data = SiteSpecificMovieData(
            id=movie_id,
            url=self._get_movie_url(movie_tile),
        )
        movie.site_data[self.site.site] = site_specific_movie_data

        self._go_to_movie_details_page(movie)
        time.sleep(1)

        iteration = 0
        while True:
            iteration += 1
            try:
                self.parse_movie_details_page(movie)
                break
            except AttributeError as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

        return movie

    def _go_to_movie_details_page(self, movie: Movie):
        self.site.open_url_with_521_retry(movie.site_data[self.site.site].url)

    @staticmethod
    def _get_movie_title(movie_tile):
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_movie_id(movie_tile):
        raise NotImplementedError("This is not the implementation you are looking for.")

    @staticmethod
    def _get_movie_url(movie_tile):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def parse_movie_details_page(self, movie: Movie):
        raise NotImplementedError("This is not the implementation you are looking for.")

    def _parse_external_links(self, movie: Movie, movie_details_page):
        external_links = self._get_external_links(movie_details_page)
        for link in external_links:
            movie_link = link["href"].strip("/").replace("http://", "https://")
            if "imdb.com" in link["href"] and "find?" not in link["href"]:
                movie.site_data[Site.IMDB] = SiteSpecificMovieData(
                    id=movie_link.split("/")[-1],
                    url=movie_link,
                )
            elif "themoviedb.org" in link["href"]:
                movie.site_data[Site.TMDB] = SiteSpecificMovieData(
                    id=movie_link.split("/")[-1],
                    url=movie_link,
                )

    @staticmethod
    def _get_external_links(movie_details_page):
        raise NotImplementedError("This is not the implementation you are looking for.")
