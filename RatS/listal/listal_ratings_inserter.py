import re
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

from RatS.base.base_ratings_inserter import RatingsInserter
from RatS.imdb.imdb_site import IMDB
from RatS.listal.listal_site import Listal
from RatS.utils import command_line


class ListalRatingsInserter(RatingsInserter):
    def __init__(self, args):
        super(ListalRatingsInserter, self).__init__(Listal(args), args)

    def _search_for_movie(self, movie: Movie):
        movie_url_path = urllib.parse.quote_plus(movie.title)
        search_url = f"https://www.listal.com/search/movies/{movie_url_path}"
        self.site.browser.get(search_url)
        self.site.handle_request_blocked_by_website()

    @staticmethod
    def _get_search_results(search_result_page):
        search_result_page = BeautifulSoup(search_result_page, "html.parser")
        return search_result_page.find_all("div", class_="itemcell")

    def _is_requested_movie(self, movie: Movie, search_result):
        self.site.browser.set_page_load_timeout(10)

        iteration = 0
        while True:
            iteration += 1
            try:
                self.site.browser.get(search_result.find("a")["href"])
                break
            except (TimeoutException, AttributeError) as e:
                if iteration > 10:
                    raise e
                self.site.browser.refresh()
                time.sleep(iteration * 1)
                continue

        time.sleep(1)
        if "imdb" in movie and movie.site_data[Site.IMDB].id != "":
            return self._compare_external_links(
                self.site.browser.page_source, movie, "imdb.com", "imdb"
            )
        else:
            return self._check_movie_details(movie)

    def _check_movie_details(self, movie: Movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        movie_annotation = movie_details_page.find(
            "h1", class_="itemheadingmedium"
        ).get_text()
        release_year = re.findall(r"\((\d{4})\)", movie_annotation)
        if release_year:
            movie_year = int(release_year[-1])
            return movie.year == movie_year
        else:
            if self.args and self.args.verbose and self.args.verbose >= 3:
                command_line.info(
                    f"{movie.title} ({movie.year}): "
                    f"No release year displayed on {self.site.site_name} movie detail page "
                    f"{self.site.browser.current_url} ... skipping "
                )
            return False

    @staticmethod
    def _compare_external_links(page_source, movie, external_url_base, site_name):
        movie_details_page = BeautifulSoup(page_source, "html.parser")
        if movie_details_page.find(class_="ratingstable"):
            external_links = movie_details_page.find(class_="ratingstable").find_all(
                "a"
            )
            for link in external_links:
                if external_url_base in link["href"]:
                    link_href = link["href"].strip("/")
                    return IMDB.normalize_imdb_id(
                        movie[site_name]["id"]
                    ) == IMDB.normalize_imdb_id(link_href.split("/")[-1])
        return False

    def _post_movie_rating(self, my_rating: int):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        movie_id = movie_details_page.find("a", class_="rateproduct")["data-productid"]

        self.site.browser.execute_script(
            """
            $.post(
                'https://www.listal.com/rate-product',
                {{
                    rating: '{my_rating}',
                    productid: '{movie_id}',
                    area: 'movies',
                    starType: 'small-star'
                }},
                function(data, status) {{}}
            );
        """.format(
                my_rating=my_rating, movie_id=movie_id
            )
        )

        time.sleep(1)
