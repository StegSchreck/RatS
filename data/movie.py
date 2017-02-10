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
