import json
import math
import re

from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.rats_exception import RatSException
from RatS.moviepilot.moviepilot_site import MoviePilot


class MoviePilotRatingsParser(RatingsParser):
    def __init__(self, args):
        super(MoviePilotRatingsParser, self).__init__(MoviePilot(args), args)

    def _get_ratings_page(self, page_number):
        return f"{self.site.MY_RATINGS_URL}?page={page_number}"

    def _retrieve_pages_count_and_movies_count(self, movie_ratings_page):
        get_session_response = self.site.browser.execute_script("""
            var xmlHttp = new XMLHttpRequest();
            xmlHttp.open( "GET", "https://www.moviepilot.de/api/session", false );
            xmlHttp.send( null );
            return xmlHttp.responseText;
        """)
        session = json.loads(get_session_response)
        if 'movie_ratings' not in session:
            self.site.browser_handler.kill()
            raise RatSException(
                f"Could not establish a session with {self.site.site_name}.\r\n"
                "Please try again with the -x option if the problem persists."
            )
        self.movies_count = session['movie_ratings']
        pages_count = math.ceil(self.movies_count / 100)
        return pages_count

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find('table').find('tbody').find_all('tr')

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find('a').get_text()

    @staticmethod
    def _get_movie_id(movie_tile):
        # handled in parse_movie_details_page
        pass

    @staticmethod
    def _get_movie_url(movie_tile):
        movie_path = movie_tile.find('a')['href']
        return f"https://www.moviepilot.de{movie_path}"

    def parse_movie_details_page(self, movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        movie['year'] = int(movie_details_page.find(attrs={'itemprop': 'copyrightYear'}).get_text())
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        json_from_script = movie_details_page.find('script', attrs={'data-hypernova-key': 'FriendsOpinionsModule'})
        movie_id = str(re.findall(r'itemId.*:(\d*),', str(json_from_script))[0])
        rating = self._get_movie_my_rating(movie_id)
        movie[self.site.site_name.lower()]['id'] = movie_id
        movie[self.site.site_name.lower()]['my_rating'] = rating

    def _get_movie_my_rating(self, movie_id):
        self.site.browser.get(f"https://www.moviepilot.de/api/movies/{movie_id}/rating")
        my_rating = self.site.get_json_from_html()
        return max(math.ceil(int(my_rating['value']) / 10), 1)
