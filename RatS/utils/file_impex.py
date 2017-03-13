import json
import os
import time

EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))


def load_movies_json(folder=EXPORTS_FOLDER, filename='import.json'):
    with open(os.path.join(folder, filename)) as file:
        movies_json = json.load(file)
        file.close()
        return [movie for movie in movies_json]


def save_movies_json(movies, folder=EXPORTS_FOLDER, filename='export.json'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+') as file:
        file.write(json.dumps(movies))
        file.close()


def wait_for_file_to_exist(filepath, seconds=30):
    for i in range(seconds):  # pylint: disable=unused-variable
        try:
            with open(filepath, 'rb') as file:
                return file
        except IOError:
            time.sleep(1)
    raise IOError('Could not access {} after {} seconds'.format(filepath, str(seconds)))
