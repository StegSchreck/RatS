import datetime
import os
import sys
import time

from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.imdb_site import IMDB
from RatS.utils import file_impex
from RatS.utils.command_line import print_progress

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
FAILED_MOVIES_FILE = TIMESTAMP + '_imdb_failed.json'


class IMDBInserter(Inserter):
    def __init__(self):
        super(IMDBInserter, self).__init__(IMDB())

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            self._post_movie_rating(movie, movie[source.lower()]['my_rating'])
            counter += 1
            print_progress(counter, len(movies), prefix=self.site.site_name)

        success_number = len(movies) - len(self.failed_movies)
        sys.stdout.write('\r\n===== %s: sucessfully posted %i of %i movies\r\n' %
                         (self.site.site_name, success_number, len(movies)))
        for failed_movie in self.failed_movies:
            sys.stdout.write('FAILED TO FIND: [IMDB:%s] %s (%i)\r\n' %
                             (failed_movie['imdb']['id'], failed_movie['title'], failed_movie['year']))
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename=FAILED_MOVIES_FILE)
            sys.stdout.write('===== %s: export data for %i failed movies to %s/%s\r\n' %
                             (self.site.site_name, len(self.failed_movies), EXPORTS_FOLDER, EXPORTS_FOLDER))
        sys.stdout.flush()

        self.site.kill_browser()

    def _post_movie_rating(self, movie, my_rating):
        self.site.browser.get(movie[self.site.site_name.lower()]['url'])
        time.sleep(1)
        try:
            self._click_rating(my_rating)
        except (ElementNotVisibleException, NoSuchElementException):
            time.sleep(3)
            self._click_rating(my_rating)

    def _click_rating(self, my_rating):
        self.site.browser.find_element_by_class_name('star-rating-button').find_element_by_tag_name('button').click()
        time.sleep(0.5)
        stars = self.site.browser.find_element_by_class_name('star-rating-stars').find_elements_by_tag_name('a')
        star_index = int(my_rating) - 1
        stars[star_index].click()
