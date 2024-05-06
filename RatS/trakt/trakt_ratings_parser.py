from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.base.movie_entity import Movie, SiteSpecificMovieData
from RatS.trakt.trakt_site import Trakt


class TraktRatingsParser(RatingsParser):
    def __init__(self, args):
        super(TraktRatingsParser, self).__init__(Trakt(args), args)

    def _get_ratings_page(self, page_number: int):
        return f"{self.site.MY_RATINGS_URL}?page={page_number}"

    @staticmethod
    def _get_movies_count(movie_ratings_page):
        return int(
            movie_ratings_page.find("section", class_="subnav-wrapper")
            .find("a", attrs={"data-title": "Movies"})
            .find("span")
            .get_text()
            .strip()
            .replace(",", "")
        )

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        ratings_section = movie_ratings_page.find(id="rating-items")
        if ratings_section:
            pagination_elements = ratings_section.find_all("li", class_="page")
            if pagination_elements:
                return int(pagination_elements[-1].find("a").get_text())
        return 1

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find(class_="row posters").find_all("div", attrs={"data-type": "movie"})

    @staticmethod
    def _get_movie_title(movie_tile):
        return movie_tile.find("h3").get_text()

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile["data-movie-id"]

    @staticmethod
    def _get_movie_url(movie_tile):
        return f"https://trakt.tv{movie_tile['data-url']}"

    def parse_movie_details_page(self, movie: Movie):
        movie_details_page = BeautifulSoup(self.site.browser.page_source, "html.parser")
        movie_year = movie_details_page.find(class_="year").get_text()
        movie.year = int(movie_year) if movie_year else 0
        if self.site.site not in movie.site_data:
            movie.site_data[self.site.site] = SiteSpecificMovieData()
        movie.site_data[self.site.site].my_rating = self._get_movie_my_rating(movie_details_page)
        self._parse_external_links(movie, movie_details_page)

    @staticmethod
    def _get_movie_my_rating(movie_details_page):
        return int(movie_details_page.find("div", class_="rated-text").find("div", class_="rating").get_text())

    @staticmethod
    def _get_external_links(movie_details_page):
        return movie_details_page.find(id="info-wrapper").find("ul", class_="external").find_all("a")
