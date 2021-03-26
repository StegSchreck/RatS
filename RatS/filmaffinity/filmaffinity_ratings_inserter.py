import time
import urllib.parse

from bs4 import BeautifulSoup

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.filmaffinity.filmaffinity_site import FilmAffinity


class FilmAffinityRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(FilmAffinityRatingsInserter, self).__init__(FilmAffinity(args), args)

    def _search_for_movie(self, movie):
        search_url = 'https://www.filmaffinity.com/en/search.php?{search_params}'.format(
            search_params=urllib.parse.urlencode({'stype': 'title', 'stext': movie['title']})
        )
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find_all('div', class_='se-it')

    def _is_movie_in_search_results(self, movie, search_results):
        if self._on_search_result_page():
            for search_result in search_results:
                if self._is_requested_movie(movie, search_result):
                    return True  # Found
        elif self._on_movie_detail_page():
            # already on movie detail page
            if self._get_displayed_movie_year() == movie['year']:
                return True
        return False  # Not Found

    def _on_search_result_page(self):
        return 'search.php' in self.site.browser.current_url

    def _on_movie_detail_page(self):
        return '/film' in self.site.browser.current_url

    def _get_displayed_movie_year(self):
        return int(self.site.browser.find_element_by_xpath("//dd[@itemProp='datePublished']").text)

    def _is_requested_movie(self, movie, search_result):
        if self._is_field_in_parsed_data_for_this_site(movie, 'id'):
            return movie[self.site.site_name.lower()]['id'] == \
                   search_result.find('div', class_='movie-card')['data-movie-id']
        else:
            return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie, search_result):
        movie_year = int(search_result.find('div', class_='ye-w').get_text())

        if movie['year'] == movie_year:
            try:
                movie_url = search_result.find('div', class_='mc-poster').find('a')['href']
                self.site.browser.get(movie_url)
                time.sleep(1)
                return True
            except KeyError:
                return False
        return False

    def _click_rating(self, my_rating):
        itk = self.site.browser.find_element_by_css_selector('.rating-select').get_attribute('data-itk')
        movie_id = self.site.browser.find_element_by_css_selector('.rate-movie-box').get_attribute('data-movie-id')

        self.site.browser.execute_script("""
            $.post(
                'https://www.filmaffinity.com/en/ratingajax.php',
                {{
                    rating: '{my_rating}',
                    id: '{movie_id}',
                    itk: '{itk}',
                    rsid: 'ui-id-2',
                    action: 'rate'
                }},
                function(data, status) {{}}
            );
        """.format(my_rating=my_rating, movie_id=movie_id, itk=itk))
        time.sleep(1)
