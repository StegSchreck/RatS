import time
import urllib.parse

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.rottentomatoes.rottentomatoes_site import RottenTomatoes


class RottenTomatoesRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(RottenTomatoesRatingsInserter, self).__init__(RottenTomatoes(args), args)

    def _search_for_movie(self, movie):
        search_url = 'https://www.rottentomatoes.com/api/private/v2.0/search?{search_params}'.format(
            search_params=urllib.parse.urlencode({'q': movie['title'], 't': 'movie'})
        )
        self.site.browser.get(search_url)

    def _get_search_results(self, search_result_page):
        json_data = self.site.get_json_from_html()
        return json_data['movies']

    def _is_requested_movie(self, movie, search_result):
        if self._is_field_in_parsed_data_for_this_site(movie, 'url'):
            return movie[self.site.site_name.lower()]['url'] == \
                   'https://www.rottentomatoes.com' + search_result['url']
        elif search_result['year'] and movie['year'] == int(search_result['year']):
            self.site.browser.get('https://www.rottentomatoes.com' + search_result['url'])
            time.sleep(1)
            return True
        return False

    def _click_rating(self, my_rating):
        converted_rating = str(my_rating / 2)
        if len(self.site.browser.find_elements_by_id('rating-root')) > 0:
            return
        movie_id = self.site.browser.find_element_by_id('rating-root').get_attribute('data-movie-id')

        self.site.browser.execute_script("""
            return $.post({
                url: 'https://www.rottentomatoes.com/napi/user/rating',
                data: { 
                    'score': """ + converted_rating + """,
                    'reviewText': '',
                    'isSuperReviewer': false,
                    'mediaType': 'movie',
                    'mediaId': """ + movie_id + """
                }
            });
        """)
        time.sleep(1)
