import datetime
import os
import sys
import time

from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException

from RatS.data import file_handler
from RatS.inserters.base_inserter import Inserter
from RatS.sites.imdb_site import IMDB
from RatS.utils.command_line import print_progress

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
FAILED_MOVIES_FILE = TIMESTAMP + '_imdb_failed.json'


class IMDBInserter(Inserter):
    def __init__(self):
        super(IMDBInserter, self).__init__(IMDB())

    def insert(self, movies):
        counter = 0
        failed_movies = []
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (type(self.site).__name__, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            imdb_entry = self._find_movie(movie)
            time.sleep(1)
            if imdb_entry:
                self._post_movie_rating(movie, movie.trakt.my_rating)
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
        if movie.imdb.url != '':
            self.site.browser.get(movie.imdb.url)
            return True
        else:
            self.site.browser.get('http://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=all' % movie.title)
            return False

    def _post_movie_rating(self, movie, my_rating):
        self.site.browser.get(movie.imdb.url)
        time.sleep(1)
        try:
            self._click_rating(my_rating)
        except (ElementNotVisibleException, NoSuchElementException):
            time.sleep(3)
            self._click_rating(my_rating)

    def _click_rating(self, my_rating):
        stars = self.site.browser.find_element_by_class_name('star-rating-stars').find_elements_by_tag_name('a')
        star_index = 10 - int(my_rating)
        stars[star_index].click()
