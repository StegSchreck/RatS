import datetime
import os
import sys
import time

import re

from bs4 import BeautifulSoup
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
            sys.stdout.write('FAILED TO FIND: %s (%i)\r\n' % (failed_movie['title'], failed_movie['year']))
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename=FAILED_MOVIES_FILE)
            sys.stdout.write('===== %s: export data for %i failed movies to %s/%s\r\n' %
                             (self.site.site_name, len(self.failed_movies), EXPORTS_FOLDER, EXPORTS_FOLDER))
        sys.stdout.flush()

        self.site.kill_browser()

    def _post_movie_rating(self, movie, my_rating):
        if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['url'] != '':
            self.site.browser.get(movie[self.site.site_name.lower()]['url'])
        else:
            movie_url = self._find_movie(movie)
            if movie_url:
                self.site.browser.get(movie_url)
            else:
                self.failed_movies.append(movie)
                return
        time.sleep(1)
        try:
            self._click_rating(my_rating)
        except (ElementNotVisibleException, NoSuchElementException):
            time.sleep(3)
            self._click_rating(my_rating)

    def _find_movie(self, movie):
        self.site.browser.get('http://www.imdb.com/find?s=tt&ref_=fn_al_tt_mr&q=%s' % movie['title'])
        time.sleep(1)
        search_result_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        search_results_list = search_result_page.find(class_='findList')
        if search_results_list:  # found something
            search_results = search_results_list.find_all(class_='findResult')
            for result in search_results:
                if self._is_requested_movie(movie, result):
                    return "http://www.imdb.com" + result.find('a')['href']

    @staticmethod
    def _is_requested_movie(movie, result):
        result_annotation = result.find(class_='result_text').get_text()
        result_year = re.findall('\((\d{4})\)', result_annotation)[-1]
        if int(result_year) == movie['year']:
            return True
        return False

    def _click_rating(self, my_rating):
        self.site.browser.find_element_by_class_name('star-rating-button').find_element_by_tag_name('button').click()
        time.sleep(0.5)
        stars = self.site.browser.find_element_by_class_name('star-rating-stars').find_elements_by_tag_name('a')
        star_index = int(my_rating) - 1
        stars[star_index].click()
