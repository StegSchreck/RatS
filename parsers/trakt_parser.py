from bs4 import BeautifulSoup

from data.movie import Movie
from parsers.base_parser import BaseParser


class TraktRatingsParser(BaseParser):
    def __init__(self):
        self.LOGIN_PAGE = 'https://trakt.tv/auth/signin'
        super(TraktRatingsParser, self).__init__()

    def parse(self):
        self.browser.get('https://trakt.tv/users/%s/ratings/movies/all/added' % self.config['Trakt']['USERNAME'])
        overview_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        self._parse_html(overview_page)
        return self.movies

    def _parse_html(self, overview):
        pages = overview.find(id='rating-items').find_all('li', class_='page')[-1].find('a').get_text()
        for i in range(1, int(pages) + 1):
            self.browser.get('https://trakt.tv/users/%s/ratings/movies/all/added?page=%i' % (self.config['Trakt']['USERNAME'], i))
            self._parse_movie_listing_page()

    def _insert_login_credentials(self):
        login_field_user = self.browser.find_element_by_xpath("//form[@id='new_user']//input[@id='user_login']")
        login_field_user.send_keys(self.config['Trakt']['USERNAME'])
        login_field_password = self.browser.find_element_by_xpath("//form[@id='new_user']//input[@id='user_password']")
        login_field_password.send_keys(self.config['Trakt']['PASSWORD'])

    def _click_login_button(self):
        login_button = self.browser.find_element_by_xpath("//form[@id='new_user']//input[@type='submit']")
        login_button.click()

    def _parse_movie_listing_page(self):
        movie_listing_page = BeautifulSoup(self.browser.page_source, 'html.parser')
        movies_tiles = movie_listing_page.find(class_='row posters').find_all('div', attrs={'data-type': 'movie'})
        for movie_tile in movies_tiles:
            self.movies.append(self._parse_movie(movie_tile))
            
    def _parse_movie(self, movie_tile):
        movie = Movie()
        movie.trakt.id = movie_tile['data-movie-id']
        movie.trakt.url = 'https://trakt.tv%s' % movie_tile['data-url']
        movie.title = movie_tile.find('h3').get_text()
        movie.trakt.my_rating = movie_tile.find_all('h4')[1].get_text().strip()

        self.browser.get(movie.trakt.url)

        movie_page = BeautifulSoup(self.browser.page_source, 'html.parser')

        movie.trakt.overall_rating = movie_page.find(id='summary-ratings-wrapper').find('ul', class_='ratings')\
            .find('li', attrs={'itemprop': 'aggregateRating'}).find('div', class_='rating').get_text()

        external_links = movie_page.find(id='info-wrapper').find('ul', class_='external').find_all('a')
        for link in external_links:
            if 'imdb.com' in link['href']:
                movie.imdb.url = link['href']
                movie.imdb.id = movie.imdb.url.split('/')[-1]
            if 'themoviedb.org' in link['href']:
                movie.tmdb.url = link['href']
                movie.tmdb.id = movie.tmdb.url.split('/')[-1]

        print("Parsing movie: %s" % movie.title)

        return movie
