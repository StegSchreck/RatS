import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.criticker_site import Criticker


class CritickerRatingsInserter(Inserter):
    def __init__(self):
        super(CritickerRatingsInserter, self).__init__(Criticker())

    def _search_for_movie(self, movie):
        self.site.browser.get('https://www.criticker.com/?search=%s&type=films' % movie['title'])

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', class_='sr_result')

    def _is_requested_movie(self, movie, search_result):
        if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['id'] != '':
            return movie[self.site.site_name.lower()]['id'] == \
                   search_result.find(_class='sr_minireview').find('textarea')['film']
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        movie_url = search_result.find(class_='sr_result_name').find('a')['href']
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
        try:
            external_links = movie_details_page.find(id='fi_info_imdb').find_all('a')
        except AttributeError:
            return False
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
