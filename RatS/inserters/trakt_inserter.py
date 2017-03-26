import datetime
import os
import sys
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.trakt_site import Trakt
from RatS.utils import file_impex
from RatS.utils.command_line import print_progress

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'RatS', 'exports'))
FAILED_MOVIES_FILE = TIMESTAMP + '_trakt_failed.json'


class TraktInserter(Inserter):
    def __init__(self):
        super(TraktInserter, self).__init__(Trakt())

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (type(self.site).__name__, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            if type(self.site).__name__.lower() in movie and movie[type(self.site).__name__.lower()]['url'] != '':
                self.site.browser.get(movie[type(self.site).__name__.lower()]['url'])
                success = True
            else:
                success = self._find_movie(movie)
            if success:
                self._post_movie_rating(movie[source.lower()]['my_rating'])
            else:
                self.failed_movies.append(movie)
            counter += 1
            print_progress(counter, len(movies), prefix=type(self.site).__name__)

        success_number = len(movies) - len(self.failed_movies)
        sys.stdout.write('\r\n===== %s: sucessfully posted %i of %i movies\r\n' %
                         (type(self.site).__name__, success_number, len(movies)))
        for failed_movie in self.failed_movies:
            sys.stdout.write('FAILED TO FIND: [IMDB:%s] %s (%i)\r\n' %
                             (failed_movie['imdb']['id'], failed_movie['title'], failed_movie['year']))
        if len(self.failed_movies) > 0:
            file_impex.save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename=FAILED_MOVIES_FILE)
            sys.stdout.write('===== %s: export data for %i failed movies to %s/%s\r\n' %
                             (type(self.site).__name__, len(self.failed_movies), EXPORTS_FOLDER, EXPORTS_FOLDER))
        sys.stdout.flush()

        self.site.kill_browser()

    def _find_movie(self, movie):
        self.site.browser.get('https://trakt.tv/search/?query=%s' % movie['title'])
        time.sleep(1)
        try:
            movie_tiles = self._get_movie_tiles(self.site.browser.page_source)
        except (NoSuchElementException, KeyError):
            time.sleep(3)
            movie_tiles = self._get_movie_tiles(self.site.browser.page_source)
        for tile in movie_tiles:
            if self._is_requested_movie(movie, tile):
                return True
        return False

    @staticmethod
    def _get_movie_tiles(overview_page):
        search_result_page = BeautifulSoup(overview_page, 'html.parser')
        return search_result_page.find_all('div', attrs={'data-type': 'movie'})

    def _is_requested_movie(self, movie, tile):
        if type(self.site).__name__.lower() in movie and movie[type(self.site).__name__.lower()]['id'] != '':
            return movie[type(self.site).__name__.lower()]['id'] == tile['data-movie-id']
        else:
            self.site.browser.get('https://trakt.tv' + tile['data-url'])
            time.sleep(1)
            movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            external_links = movie_details_page.find(id='info-wrapper').find('ul', class_='external').find_all('a')
            for link in external_links:
                if 'imdb.com' in link['href']:
                    return movie['imdb']['id'] == link['href'].split('/')[-1]

    def _post_movie_rating(self, my_rating):
        try:
            self._click_rating(my_rating)
        except (ElementNotVisibleException, NoSuchElementException):
            time.sleep(3)
            self._click_rating(my_rating)

    def _click_rating(self, my_rating):
        self.site.browser.find_element_by_class_name('summary-user-rating').click()
        time.sleep(1)
        star_index = 10 - int(my_rating)
        self.site.browser.execute_script("$('.rating-hearts').find('label')[%i].click()" % star_index)
