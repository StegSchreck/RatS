from data.movie_source import MovieSource


class Movie:
    def __str__(self):
        return "%s (Trakt:%s) (IMDB:%s) (TMDB:%s) (MovieLense:%s) (RottenTomato:%s)" % \
               (self.title, self.trakt, self.imdb, self.tmdb, self.movielense, self.rottentomato)

    title = ''

    imdb = MovieSource()
    trakt = MovieSource()
    tmdb = MovieSource()
    movielense = MovieSource()
    rottentomato = MovieSource()

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
