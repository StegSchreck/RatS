import time

from bs4 import BeautifulSoup

from RatS.inserters.base_inserter import Inserter
from RatS.sites.trakt_site import Trakt


class TraktRatingsInserter(Inserter):
    def __init__(self, args):
        super(TraktRatingsInserter, self).__init__(Trakt(), args)

    def _search_for_movie(self, movie):
        self.site.browser.get('https://trakt.tv/search/?query=%s' % movie['title'])

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', attrs={'data-type': 'movie'})

    def _is_requested_movie(self, movie, search_result):
        if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['id'] != '':
            return movie[self.site.site_name.lower()]['id'] == search_result['data-movie-id']
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        self.site.browser.get('https://trakt.tv' + search_result['data-url'])
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

    def _click_rating(self, my_rating):
        self.site.browser.find_element_by_class_name('summary-user-rating').click()
        time.sleep(1)
        star_index = 10 - int(my_rating)
        self.site.browser.execute_script("$('.rating-hearts').find('label')[%i].click()" % star_index)
