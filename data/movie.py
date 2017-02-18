from data.movie_source import MovieSource


class Movie:
    def __init__(self):
        self.title = ''

        self.imdb = MovieSource()
        self.trakt = MovieSource()
        self.tmdb = MovieSource()
        self.movielense = MovieSource()
        self.rottentomato = MovieSource()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return True

    def __str__(self):
        return "%s (Trakt:%s) (IMDB:%s) (TMDB:%s) (MovieLense:%s) (RottenTomato:%s)" % \
               (self.title, self.trakt, self.imdb, self.tmdb, self.movielense, self.rottentomato)

    def to_json(self):
        movie_json = {
            'title': self.title,
            'imdb': self.imdb.to_json(),
            'trakt': self.trakt.to_json(),
            'tmdb': self.tmdb.to_json(),
            'movielense': self.movielense.to_json(),
            'rottentomato': self.rottentomato.to_json()
        }
        return movie_json

    @staticmethod
    def from_json(json):
        movie = Movie()
        movie.title = json['title']
        movie.imdb = MovieSource.from_json(json['imdb'])
        movie.trakt = MovieSource.from_json(json['trakt'])
        movie.tmdb = MovieSource.from_json(json['tmdb'])
        movie.movielense = MovieSource.from_json(json['movielense'])
        movie.rottentomato = MovieSource.from_json(json['rottentomato'])
        return movie
