import sys
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.trakt_site import Trakt
from RatS.utils.command_line import print_progress


class TraktInserter(Inserter):
    def __init__(self):
        super(TraktInserter, self).__init__(Trakt())

    def insert(self, movies, source):
        counter = 0
        sys.stdout.write('\r===== %s: posting %i movies\r\n' % (self.site.site_name, len(movies)))
        sys.stdout.flush()

        for movie in movies:
            if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['url'] != '':
                self.site.browser.get(movie[self.site.site_name.lower()]['url'])
                success = True
            else:
                success = self._find_movie(movie)
            if success:
                self._post_movie_rating(movie[source.lower()]['my_rating'])
            else:
                self.failed_movies.append(movie)
            counter += 1
            print_progress(counter, len(movies), prefix=self.site.site_name)

        self._print_summary(movies)
        self._handle_failed_movies(movies)
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
                return True  # Found
        return False  # Not Found

    @staticmethod
    def _get_movie_tiles(overview_page):
        search_result_page = BeautifulSoup(overview_page, 'html.parser')
        return search_result_page.find_all('div', attrs={'data-type': 'movie'})

    def _is_requested_movie(self, movie, tile):
        if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['id'] != '':
            return movie[self.site.site_name.lower()]['id'] == tile['data-movie-id']
        else:
            return self._check_movie_details(movie, tile)

    def _check_movie_details(self, movie, tile):
        self.site.browser.get('https://trakt.tv' + tile['data-url'])
        time.sleep(1)
        if 'imdb' in movie and movie['imdb']['id'] != '':
            return self._compare_external_links(self.site.browser.page_source, movie, 'imdb.com', 'imdb')
        elif 'tmdb' in movie and movie['tmdb']['id'] != '':
            return self._compare_external_links(self.site.browser.page_source, movie, 'themoviedb.org', 'tmdb')
        else:
            movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            return movie['year'] == int(movie_details_page.find(class_='year').get_text())

    @staticmethod
    def _compare_external_links(page_source, movie, external_url_base, site_name):
        movie_details_page = BeautifulSoup(page_source, 'html.parser')
        external_links = movie_details_page.find(id='info-wrapper').find('ul', class_='external').find_all('a')
        for link in external_links:
            if external_url_base in link['href']:
                return movie[site_name]['id'] == link['href'].split('/')[-1]

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
