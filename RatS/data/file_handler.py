import json
import os

from RatS.data.movie import Movie


def load_movies_json(filename):
    with open(filename) as file:
        movies_json = json.load(file)
        file.close()
        return [Movie.from_json(movie) for movie in movies_json]


def save_movies_json(movies_to_save, folder, filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+') as file:
        movies_json = [movie.to_json() for movie in movies_to_save]
        file.write(json.dumps(movies_json))
        file.close()
