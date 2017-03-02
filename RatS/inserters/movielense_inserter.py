import json
import os
import time

import sys

import datetime
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException

from RatS.data import file_handler
from RatS.inserters.base_inserter import Inserter
from RatS.sites.movielense_site import Movielense
from RatS.utils.command_line import print_progress

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))
FAILED_MOVIES_FILE = TIMESTAMP + '_movielense_failed.json'


class MovielenseInserter(Inserter):
    def __init__(self):
        super(MovielenseInserter, self).__init__(Movielense())

    def insert(self, movies):
        counter = 0
        failed_movies = []
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (type(self.site).__name__, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            movielense_entry = self._find_movie(movie)
            if movielense_entry:
                self._post_movie_rating(movielense_entry, movie.trakt.my_rating)
            else:
                failed_movies.append(movie)
            counter += 1
            print_progress(counter, len(movies), prefix=type(self.site).__name__)

        success_number = len(movies) - len(failed_movies)
        sys.stdout.write('\r\n===== %s: sucessfully posted %i of %i movies\r\n' %
                         (type(self.site).__name__, success_number, len(movies)))
        for failed_movie in failed_movies:
            sys.stdout.write('FAILED TO FIND: [IMDB:%s] %s\r\n' % (failed_movie.imdb.id, failed_movie.title))
        file_handler.save_movies_json(movies, folder=EXPORTS_FOLDER, filename=FAILED_MOVIES_FILE)
        sys.stdout.write('===== %s: export data for %i failed movies to %s/%s\r\n' %
                         (type(self.site).__name__, len(failed_movies), EXPORTS_FOLDER, EXPORTS_FOLDER))
        sys.stdout.flush()

        self.site.kill_browser()

    def _find_movie(self, movie):
        self.site.browser.get('https://movielens.org/api/movies/explore?q=%s' % movie.title)
        time.sleep(1)
        try:
            search_results = self._get_json_from_html()
        except (NoSuchElementException, KeyError):
            time.sleep(3)
            search_results = self._get_json_from_html()
        for search_result in search_results:
            if self._is_requested_movie(movie, search_result['movie']):
                return search_result['movie']

    def _get_json_from_html(self):
        response = self.site.browser.find_element_by_tag_name("pre").text
        json_data = json.loads(response)
        return json_data['data']['searchResults']

    @staticmethod
    def _is_requested_movie(movie, param):
        if movie.movielense.id != '':
            return movie.movielense.id == param['movieId']
        else:
            return movie.imdb.id.replace('tt', '') == param['imdbMovieId'].replace('tt', '')

    def _post_movie_rating(self, movielense_entry, my_rating):
        movie_page_url = 'https://movielens.org/movies/%s' % str(movielense_entry['movieId'])
        self.site.browser.get(movie_page_url)
        time.sleep(1)
        try:
            self._click_rating(my_rating)
        except (ElementNotVisibleException, NoSuchElementException):
            time.sleep(3)
            self._click_rating(my_rating)

    def _click_rating(self, my_rating):
        stars = self.site.browser.find_element_by_class_name('rating').find_elements_by_tag_name('span')
        star_index = 10 - int(my_rating)
        stars[star_index].click()
