import csv
import json
import os
import time

import sys

EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))
CSV_HEADER = '"position","const","created","modified","description","Title","Title type","Directors","You rated","IMDb Rating","Runtime (mins)","Year","Genres","Num. Votes","Release Date (month/day/year)","URL"\n'  # pylint: disable=line-too-long


def load_movies_from_json(folder=EXPORTS_FOLDER, filename='import.json'):
    with open(os.path.join(folder, filename)) as input_file:
        movies_json = json.load(input_file)
        return [movie for movie in movies_json]


def save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename='export.json'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+') as output_file:
        output_file.write(json.dumps(movies))


def wait_for_file_to_exist(filepath, seconds=30):
    for i in range(seconds):  # pylint: disable=unused-variable
        try:
            with open(filepath, 'rb') as file:
                return file
        except IOError:
            time.sleep(1)
    raise IOError('Could not access {} after {} seconds'.format(filepath, str(seconds)))


def load_movies_from_csv(filepath):
    sys.stdout.write('===== getting movies from CSV\r\n')
    sys.stdout.flush()
    wait_for_file_to_exist(filepath)
    with open(filepath, newline='') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        next(reader, None)  # ignore csv header
        return [convert_csv_row_to_movie(row) for row in reader]


def convert_csv_row_to_movie(row):
    movie = dict()
    movie['title'] = row[5]
    movie['year'] = row[11]
    movie['imdb'] = dict()
    movie['imdb']['id'] = row[1]
    movie['imdb']['url'] = row[15]
    movie['imdb']['my_rating'] = row[8]
    movie['imdb']['overall_rating'] = row[9]
    return movie


def save_movies_to_csv(movies, folder=EXPORTS_FOLDER, filename='export.csv', rating_source='imdb'):
    sys.stdout.write('===== saving movies to CSV\r\n')
    sys.stdout.flush()
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+') as output_file:
        output_file.write(CSV_HEADER)
        for i in range(len(movies)):
            output_file.write(convert_movie_to_csv(movies, i, rating_source) + '\n')


def convert_movie_to_csv(movies, index, rating_source):
    movie_csv = str(index) + ',' + \
                movies[index]['imdb']['id'] + ',' + \
                ',' + \
                ',' + \
                ',' + \
                movies[index]['title'] + ',' + \
                'Feature Film,' + \
                ',' + \
                str(movies[index][rating_source]['my_rating']) + ',' + \
                ',' + \
                ',' + \
                str(movies[index]['year']) + ',' + \
                ',' + \
                ',' + \
                ',' + \
                movies[index]['imdb']['url']
    return movie_csv
