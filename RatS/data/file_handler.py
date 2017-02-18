import csv
import json

from RatS.data.movie import Movie


def load_movies_json(filename):
    with open(filename) as file:
        movies_json = json.load(file)
        file.close()
        return [Movie.from_json(movie) for movie in movies_json]


def save_movies_json(movies_to_save, filename):
    with open(filename, 'w') as file:
        movies_json = [movie.to_json() for movie in movies_to_save]
        file.write(json.dumps(movies_json))
        file.close()


def save_movies_to_csv(movies_to_save, filename):
    movies_json = [movie.to_json() for movie in movies_to_save]
    with open(filename, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'imdb', 'trakt', 'tmdb', 'movielense', 'rottentomato'])
        writer.writeheader()
        writer.writerows(movies_json)
        file.close()
