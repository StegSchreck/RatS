import csv
import datetime
import json
import os
import sys
import time
import zipfile

EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))
CSV_HEADER = 'Const,Your Rating,Date Rated,Title,URL,Title Type,IMDb Rating,Runtime (mins),Year,Genres,Num Votes,Release Date,Directors\n'  # pylint: disable=line-too-long


def load_movies_from_json(folder=EXPORTS_FOLDER, filename='import.json'):
    with open(os.path.join(folder, filename), encoding='UTF-8') as input_file:
        return json.load(input_file)


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


def load_movies_from_csv(filepath, encoding='UTF-8'):
    sys.stdout.write('===== getting movies from CSV\r\n')
    sys.stdout.flush()
    wait_for_file_to_exist(filepath)
    with open(filepath, newline='', encoding=encoding) as input_file:
        reader = csv.reader(input_file, delimiter=',')
        headers = next(reader, None)
        return [convert_csv_row_to_movie(headers, row) for row in reader]


def convert_csv_row_to_movie(headers, row):
    movie = dict()
    movie['title'] = row[headers.index("Title")]
    movie['year'] = int(row[headers.index("Year")])
    movie['imdb'] = dict()
    movie['imdb']['id'] = row[headers.index("Const")]
    movie['imdb']['url'] = row[headers.index("URL")].replace('http://', 'https://')
    movie['imdb']['my_rating'] = int(row[headers.index("Your Rating")])
    return movie


def save_movies_to_csv(movies, folder=EXPORTS_FOLDER, filename='export.csv', rating_source='imdb'):
    sys.stdout.write('===== saving movies to CSV\r\n')
    sys.stdout.flush()
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(os.path.join(folder, filename), 'w+', encoding='UTF-8') as output_file:
        output_file.write(CSV_HEADER)
        for i in range(len(movies)):
            output_file.write(convert_movie_to_csv(movies, i, rating_source))


def convert_movie_to_csv(movies, index, rating_source):
    imdb_id = movies[index]['imdb']['id'] if 'imdb' in movies[index] else ''
    imdb_url = movies[index]['imdb']['url'] if 'imdb' in movies[index] else ''
    movie_csv = '' + \
                '' + imdb_id + ',' + \
                '' + str(movies[index][rating_source.lower()]['my_rating']) + ',' + \
                '' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + ',' + \
                '"' + movies[index]['title'] + '",' + \
                '' + imdb_url + ',' + \
                'movie,' + \
                ',' + \
                ',' + \
                '' + str(movies[index]['year']) + ',' + \
                ',' + \
                ',' + \
                '' + str(movies[index]['year']) + '-01-01,' + \
                '' + \
                '\n'
    return movie_csv


def extract_file_from_archive(path_to_zip_file, filename_to_extract, directory_to_extract_to):
    if not os.path.exists(directory_to_extract_to):
        os.makedirs(directory_to_extract_to)
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extract(filename_to_extract, directory_to_extract_to)
    zip_ref.close()
    os.remove(path_to_zip_file)
