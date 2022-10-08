import re
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.flixster.flixster_site import Flixster


class FlixsterRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(FlixsterRatingsInserter, self).__init__(Flixster(args), args)

    def _find_movie(self, movie):
        directly_found = self._search_for_movie(movie)

        if directly_found:
            return True
        elif self._is_empty_search_result() or self._is_internal_server_error():
            return False  # no search results

        try:
            self.site.browser.find_element(
                By.XPATH, "//a[@href='#results_movies_tab']"
            ).click()
        except NoSuchElementException:
            return False

        time.sleep(1)
        return self._process_search_results(movie)

    def _process_search_results(self, movie):
        iteration = 0
        search_results = None
        while not search_results:
            iteration += 1
            try:
                search_results = self._get_search_results(self.site.browser.page_source)
            except (NoSuchElementException, KeyError) as e:
                if iteration > 10:
                    raise e
                time.sleep(iteration * 1)
                continue

        for search_result in search_results:
            if self._is_requested_movie(movie, search_result):
                return True  # Found
        return False  # Not Found in search results

    def _is_empty_search_result(self):
        return (
            "Sorry, no results found for"
            in self.site.browser.find_element(By.TAG_NAME, "h1").text
        )

    def _is_internal_server_error(self):
        return (
            "Sorry, we're having some technical difficulties"
            in self.site.browser.find_element(By.TAG_NAME, "h1").text
        )

    def _search_for_movie(self, movie):
        search_params = urllib.parse.urlencode({"search": movie["title"]})
        search_url = f"https://www.flixster.com/search/?{search_params}"
        self.site.browser.get(search_url)
        time.sleep(1)
        return (
            "/movie/" in self.site.browser.current_url
        )  # already on movie_details_page

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        return search_result_page.find("ul", id="movie_results_ul").find_all(
            "li", class_="media"
        )

    def _is_requested_movie(self, movie, search_result):
        movie_heading = search_result.find("p", class_="heading").find("a")
        movie_url = "https://www.flixster.com" + movie_heading["href"]
        if self._is_field_in_parsed_data_for_this_site(movie, "url"):
            success = movie[self.site.site_name.lower()]["url"] == movie_url
        else:
            try:
                success = movie["year"] == int(
                    re.findall(r"\((\d{4})\)", movie_heading.get_text())[-1]
                )
            except IndexError:
                return False
        if success:
            self.site.browser.get(movie_url)
            time.sleep(1)
        return success

    def _click_rating(self, my_rating):
        movie_id = self.site.browser.find_element(
            By.XPATH, "//meta[@name='movieID']"
        ).get_attribute("content")
        converted_rating = str(float(my_rating) / 2)

        rating_script = self._get_insert_javascript_template().format(
            movie_id=movie_id,
            user_id=str(self.site.USERID),
            movie_url=self.site.browser.current_url,
            rating=converted_rating,
        )

        self.site.browser.execute_script(rating_script)

    @staticmethod
    def _get_insert_javascript_template():
        return """
            $.post(
                'https://www.flixster.com/api/users/current/movies/ratings/{movie_id}',
                {{
                    id: '{user_id}_{movie_id}',
                    movieId: '{movie_id}',
                    lastUpdated: '0 minutes ago',
                    movieUrl: '{movie_url}',
                    ratingSource: 'Flixster',
                    review: '',
                    score: '{rating}',
                    user: {{
                        firstName: '',
                        id: {user_id},
                        lastName: '',
                        thumbnailUrl: '//legacy-static.flixster.com/static/images/actor.default.tmb.gif'
                    }}
                }},
                function(data, status) {{}}
            );
        """
