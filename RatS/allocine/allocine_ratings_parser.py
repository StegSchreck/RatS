import re

from bs4 import BeautifulSoup

from RatS.base.base_ratings_parser import RatingsParser
from RatS.allocine.allocine_site import AlloCine


class AlloCineRatingsParser(RatingsParser):
    def __init__(self, args):
        super(AlloCineRatingsParser, self).__init__(AlloCine(args), args)

    def _get_ratings_page(self, i):
        return '{url}?page={page_number}'.format(url=self.site.MY_RATINGS_URL, page_number=i)

    def _retrieve_pages_count_and_movies_count(self, movie_ratings_page):
        pages_count = self._get_pages_count(movie_ratings_page)
        # Only add the number of movie on the last page
        self.site.browser.get(self._get_ratings_page(pages_count))
        last_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
        last_page_count = len(last_page.find_all('div', class_='card'))
        self.movies_count = (pages_count - 1) * 36 + last_page_count
        return pages_count

    @staticmethod
    def _get_pages_count(movie_ratings_page):
        pages_count = 1
        pagination_holder = movie_ratings_page.find('div', class_='pagination-item-holder')
        if pagination_holder:
            pages_count = max(list(map(lambda tag: int(tag.text), pagination_holder.find_all('a', text=True))))

        return pages_count

    @staticmethod
    def _get_movie_tiles(movie_listing_page):
        return movie_listing_page.find_all('div', class_='card')

    @staticmethod
    def _get_movie_title(movie_tile):
        # At this point we only see the French translation of the movie title.
        # Therefore, the original movie title is parsed later on the movie details page using _get_movie_original_title
        pass

    @staticmethod
    def _get_movie_id(movie_tile):
        return movie_tile.find('a', class_='meta-title-link')['href']\
            .replace('/film/fichefilm_gen_cfilm=', '')\
            .replace('.html', '')

    @staticmethod
    def _get_movie_url(movie_tile):
        movie_path = movie_tile.find('a', class_='meta-title-link')['href']
        return 'http://www.allocine.fr{movie_path}'.format(movie_path=movie_path)

    def parse_movie_details_page(self, movie):
        rating = 0
        iteration = 0
        movie_details_page = None
        while rating == 0:
            iteration += 1
            if iteration > 10:
                movie = None
                return
            movie_details_page = BeautifulSoup(self.site.browser.page_source, 'html.parser')
            rating = self._get_movie_my_rating(movie_details_page)

        movie['year'] = self._get_movie_year(movie_details_page)
        movie['title'] = self._get_movie_original_title(movie_details_page)
        if self.site.site_name.lower() not in movie:
            movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['my_rating'] = rating

    @staticmethod
    def _get_movie_year(movie_details_page):
        release_date_text = movie_details_page.find(class_='date').get_text()
        if release_date_text:
            result_year_list = re.findall(r'(\d{4})', release_date_text)
            if len(result_year_list) > 0:
                result_year = result_year_list[-1]
                return int(result_year)
        return 0

    @staticmethod
    def _get_movie_original_title(movie_details_page):
        original_title = movie_details_page.find('span', class_='what', text=' Titre original ')
        if original_title:
            return original_title.parent.find(class_='that').text
        else:
            return movie_details_page.find('div', class_='titlebar-title-lg').text

    @staticmethod
    def _get_movie_my_rating(movie_details_page):
        # AlloCine let you rate a movie out of 5 star but you can use half stars, so we get a note out of 10
        return len(movie_details_page.find('div', class_='user-rating-holder').find_all('div', class_='active'))
