import sys
import time

from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.movielens_site import Movielens
from RatS.utils import file_impex
from RatS.utils.command_line import print_progress


class MovielensInserter(Inserter):
    def __init__(self):
        super(MovielensInserter, self).__init__(Movielens())

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            entry = self._find_movie(movie)
            if entry:
                self._post_movie_rating(entry, movie[source.lower()]['my_rating'])
            else:
                self.failed_movies.append(movie)
            counter += 1
            print_progress(counter, len(movies), prefix=self.site.site_name)

        self._print_summary(movies)
        self._handle_failed_movies(movies)
        self.site.kill_browser()

    def _find_movie(self, movie):
        self.site.browser.get('https://movielens.org/api/movies/explore?q=%s' % movie['title'])
        time.sleep(1)
        try:
            search_results = self.site.get_json_from_html()['searchResults']
        except (NoSuchElementException, KeyError):
            time.sleep(3)
            search_results = self.site.get_json_from_html()['searchResults']
        for search_result in search_results:
            if self._is_requested_movie(movie, search_result['movie']):
                return search_result['movie']

    @staticmethod
    def _is_requested_movie(movie, param):
        if 'movielens' in movie and movie['movielens']['id'] != '':
            return movie['movielens']['id'] == param['movieId']
        elif 'imdb' in movie and movie['imdb']['id'] != '':
            return movie['imdb']['id'].replace('tt', '') == param['imdbMovieId'].replace('tt', '')
        elif 'tmdb' in movie and movie['tmdb']['id'] != '':
            return movie['tmdb']['id'] == param['tmdbMovieId']
        else:
            return movie['year'] == param['releaseYear']

    def _post_movie_rating(self, entry, my_rating):
        movie_page_url = 'https://movielens.org/movies/%s' % str(entry['movieId'])
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
