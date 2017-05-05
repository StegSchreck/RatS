import re
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from RatS.inserters.base_inserter import Inserter
from RatS.sites.flixster_site import Flixster


class FlixsterInserter(Inserter):
    def __init__(self):
        super(FlixsterInserter, self).__init__(Flixster())

    def _find_movie(self, movie):
        directly_found = self._search_for_movie(movie)

        if directly_found:
            return True
        elif 'Sorry, no results found for' in self.site.browser.find_element_by_tag_name('h1').text:
            return False  # no search results

        self.site.browser.find_element_by_xpath("//a[@href='#results_movies_tab']").click()
        time.sleep(1)
        try:
            search_results = self._get_search_results(self.site.browser.page_source)
        except (NoSuchElementException, KeyError):
            time.sleep(3)
            search_results = self._get_search_results(self.site.browser.page_source)
        for search_result in search_results:
            if self._is_requested_movie(movie, search_result):
                return True  # Found
        return False  # Not Found in search results

    def _search_for_movie(self, movie):
        self.site.browser.get('https://www.flixster.com/search/?search=%s' % movie['title'])
        time.sleep(1)
        return '/movie/' in self.site.browser.current_url  # already on movie_details_page

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, 'html.parser')
        return search_result_page.find('ul', id='movie_results_ul').find_all('li', class_='media')

    def _is_requested_movie(self, movie, search_result):
        movie_heading = search_result.find('p', class_='heading').find('a')
        movie_url = 'https://www.flixster.com' + movie_heading['href']
        if self.site.site_name.lower() in movie and movie[self.site.site_name.lower()]['url'] != '':
            success = movie[self.site.site_name.lower()]['url'] == movie_url
        else:
            success = movie['year'] == int(re.findall(r'\((\d{4})\)', movie_heading.get_text())[-1])
        if success:
            self.site.browser.get(movie_url)
            time.sleep(1)
        return success

    def _click_rating(self, my_rating):
        print(self.site.browser.page_source)
        movie_id = self.site.browser.find_element_by_xpath("//meta[@name='movieID']").get_attribute('content')
        converted_rating = str(float(my_rating)/2)

        rating_script = """
            $.post(
                'https://www.flixster.com/api/users/current/movies/ratings/%s',
                {
                    id: '%s_%s',
                    movieId: '%s',
                    lastUpdated: '0 minutes ago',
                    movieUrl: '%s',
                    ratingSource: 'Flixster',
                    review: '',
                    score: '%s',
                    user: {
                        firstName: '',
                        id: %s,
                        lastName: '',
                        thumbnailUrl: '//legacy-static.flixster.com/static/images/actor.default.tmb.gif'
                    }
                },
                function(data, status) {}
            );
        """ % (
            movie_id,
            str(self.site.USERID), movie_id,
            movie_id,
            self.site.browser.current_url,
            converted_rating,
            str(self.site.USERID)
        )

        self.site.browser.execute_script(rating_script)
