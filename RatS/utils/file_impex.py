import csv
import json
import os
import sys
import time
import zipfile

EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))
CSV_HEADER = '"position","const","created","modified","description","Title","Title type","Directors","You rated","IMDb Rating","Runtime (mins)","Year","Genres","Num. Votes","Release Date (month/day/year)","URL"\n'  # pylint: disable=line-too-long


def load_movies_from_json(folder=EXPORTS_FOLDER, filename='import.json'):
    with open(os.path.join(folder, filename), encoding='UTF-8') as input_file:
        movies_json = json.load(input_file)
        return [movie for movie in movies_json]


def save_movies_to_json(movies, folder=EXPORTS_FOLDER, filename='export.json'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+', encoding='UTF-8') as output_file:
        output_file.write(json.dumps(movies))


def wait_for_file_to_exist(filepath, seconds=30):
    iteration = 0
    while iteration < seconds:
        iteration += 1
        try:
            with open(filepath, 'rb') as file:
                return file
        except IOError:
            time.sleep(1)  # try every second
            continue
    raise IOError('Could not access {filepath} after {seconds} seconds'.format(filepath=filepath, seconds=str(seconds)))


def load_movies_from_csv(filepath):
    sys.stdout.write('===== getting movies from CSV\r\n')
    sys.stdout.flush()
    wait_for_file_to_exist(filepath)
    with open(filepath, newline='', encoding='UTF-8') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        next(reader, None)  # ignore csv header
        return [convert_csv_row_to_movie(row) for row in reader]


def convert_csv_row_to_movie(row):
    movie = dict()
    movie['title'] = row[5]
    movie['year'] = int(row[11])
    movie['imdb'] = dict()
    movie['imdb']['id'] = row[1]
    movie['imdb']['url'] = row[15]
    movie['imdb']['my_rating'] = int(row[8])
    return movie


def save_movies_to_csv(movies, folder=EXPORTS_FOLDER, filename='export.csv', rating_source='imdb'):
    sys.stdout.write('===== saving movies to CSV\r\n')
    sys.stdout.flush()
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+', encoding='UTF-8') as output_file:
        output_file.write(CSV_HEADER)
        for i in range(len(movies)):
            output_file.write(convert_movie_to_csv(movies, i, rating_source) + '\n')


def convert_movie_to_csv(movies, index, rating_source):
    imdb_id = movies[index]['imdb']['id'] if 'imdb' in movies[index] else ''
    imdb_url = movies[index]['imdb']['url'] if 'imdb' in movies[index] else ''
    movie_csv = '"' + str(index) + '",' + \
                '"' + imdb_id + '",' + \
                '"",' + \
                '"",' + \
                '"",' + \
                '"' + movies[index]['title'] + '",' + \
                '"Feature Film",' + \
                '"",' + \
                '"' + str(movies[index][rating_source.lower()]['my_rating']) + '",' + \
                '"",' + \
                '"",' + \
                '"' + str(movies[index]['year']) + '",' + \
                '"",' + \
                '"",' + \
                '"",' + \
                '"' + imdb_url + '"'
    return movie_csv


def extract_file_from_archive(path_to_zip_file, filename_to_extract, directory_to_extract_to):
    if not os.path.exists(directory_to_extract_to):
        os.makedirs(directory_to_extract_to)
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extract(filename_to_extract, directory_to_extract_to)
    zip_ref.close()
    os.remove(path_to_zip_file)
