import sys
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.criticker_site import Criticker
from RatS.utils.command_line import print_progress


class CritickerInserter(Inserter):
    def __init__(self):
        super(CritickerInserter, self).__init__(Criticker())

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
        self.site.browser.get('https://www.criticker.com/?search=%s&type=films' % movie['title'])
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
        return search_result_page.find_all('div', class_='sr_result')

    def _is_requested_movie(self, movie, tile):
        if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['id'] != '':
            return movie[self.site.site_name.lower()]['id'] == \
                   tile.find(_class='sr_minireview').find('textarea')['film']
        else:
            return self._check_movie_details(movie, tile)

    def _check_movie_details(self, movie, tile):
        movie_url = tile.find('img').parent['href']
        self.site.browser.get(movie_url)
        time.sleep(1)
        if 'imdb' in movie and movie['imdb']['id'] != '':
            return self._compare_external_links(self.site.browser.page_source, movie, 'imdb.com', 'imdb')
        else:
            movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            year = movie_details_page.find('h1').find_all('span')[1].get_text()
            return movie['year'] == int(year)

    @staticmethod
    def _compare_external_links(page_source, movie, external_url_base, site_name):
        movie_details_page = BeautifulSoup(page_source, 'html.parser')
        external_links = movie_details_page.find(id='fi_info_imdb').find_all('a')
        for link in external_links:
            if external_url_base in link['href']:
                return movie[site_name]['id'] == link['href'].split('/')[-1]

    def _post_movie_rating(self, my_rating):
        converted_rating = str(my_rating * 10)
        try:
            score = self.site.browser.find_element_by_id('fi_score_div')
            if score.is_displayed() and not score.text == converted_rating:  # already rated
                self.site.browser.find_element_by_id('fi_editscore_link').click()
                self._insert_rating(converted_rating)
        except NoSuchElementException:  # not rated yet
            self._insert_rating(converted_rating)

    def _insert_rating(self, converted_rating):
        self.site.browser.find_element_by_xpath("//input[@class='score_box']").send_keys(str(converted_rating))
        self.site.browser.find_element_by_id('fi_submit_link').click()
