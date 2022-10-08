import re
import time
import urllib.parse

from bs4 import BeautifulSoup

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.base.movie_entity import Movie
from RatS.moviepilot.moviepilot_site import MoviePilot


class MoviePilotRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(MoviePilotRatingsInserter, self).__init__(MoviePilot(args), args)

    def _search_for_movie(self, movie: Movie):
        search_params = urllib.parse.urlencode({"q": movie.title, "type": "movie"})
        search_url = f"https://www.moviepilot.de/suche?{search_params}"
        self.site.browser.get(search_url)

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        if search_result_page.find("main").find("ul"):
            return search_result_page.find("main").find("ul").find_all("a")
        return []

    def _is_requested_movie(self, movie: Movie, search_result):
        return self._check_movie_details(movie, search_result)

    def _check_movie_details(self, movie: Movie, search_result):
        try:
            movie_url = "https://www.moviepilot.de" + search_result["href"]
        except KeyError:
            return False

        self.site.browser.get(movie_url)
        time.sleep(1)
        movie_details_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        copyright_year = movie_details_page.find(attrs={"itemprop": "copyrightYear"})
        if copyright_year:
            return movie.year == int(copyright_year.get_text())
        return False

    def _post_movie_rating(self, my_rating: int):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        json_from_script = movie_details_page.find(
            "script", attrs={"data-hypernova-key": "FriendsOpinionsModule"}
        ).get_text()
        movie_id = str(re.findall(r"itemId.*:(\d*),", json_from_script)[0])

        converted_rating = str(my_rating * 10)

        self.site.browser.execute_script(
            """
            var xmlHttp = new XMLHttpRequest();
            xmlHttp.open( 'DELETE', 'https://www.moviepilot.de/api/movies/"""
            + movie_id
            + """/rating', false );
            xmlHttp.send( null );
            return xmlHttp.responseText;
        """
        )
        time.sleep(0.2)

        self.site.browser.execute_script(
            """
            var xmlHttp = new XMLHttpRequest();
            xmlHttp.open( 'POST', 'https://www.moviepilot.de/api/movies/"""
            + movie_id
            + """/rating', false );
            xmlHttp.setRequestHeader("Content-Type", "application/json;charset=utf-8");
            xmlHttp.send( JSON.stringify({ 'rating': { 'value': """
            + converted_rating
            + """} }) );
            return xmlHttp.responseText;
        """
        )
        time.sleep(0.2)
