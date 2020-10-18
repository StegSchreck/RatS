import time
import urllib.parse

from bs4 import BeautifulSoup

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.imdb.imdb_site import IMDB
from RatS.trakt.trakt_site import Trakt


class TraktRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(TraktRatingsInserter, self).__init__(Trakt(args), args)

    def _search_for_movie(self, movie):
        search_url = 'https://trakt.tv/search/?{search_params}'.format(
            search_params=urllib.parse.urlencode({'query': movie['title']})
        )
        self.site.open_url_with_521_retry(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', attrs={'data-type': 'movie'})

    def _is_requested_movie(self, movie, search_result):
        if self._is_field_in_parsed_data_for_this_site(movie, 'id'):
            return movie[self.site.site_name.lower()]['id'] == search_result['data-movie-id']
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        try:
            movie_url = 'https://trakt.tv' + search_result['data-url']
        except KeyError:
            return False

        self.site.open_url_with_521_retry(movie_url)
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
                if site_name == 'imdb':
                    return IMDB.normalize_imdb_id(movie['imdb']['id']) == \
                           IMDB.normalize_imdb_id(link['href'].split('/')[-1])
                return movie[site_name]['id'] == link['href'].split('/')[-1]
        return False

    def _click_rating(self, my_rating):
        user_rating_section = self.site.browser.find_element_by_class_name('summary-user-rating')
        user_rating = user_rating_section.find_element_by_class_name('number').find_elements_by_class_name('rating')
        if user_rating:
            current_rating = int(user_rating[0].text)
        else:
            current_rating = 0
        if current_rating is not my_rating:  # prevent un-rating if same score
            user_rating_section.click()
            time.sleep(1)
            star_index = 10 - int(my_rating)
            self.site.browser.execute_script("$('.rating-hearts').find('label')[{star_index}].click()".format(
                star_index=star_index
            ))
