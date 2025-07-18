import fileinput
import glob
import os
import re
from shutil import copyfile

from selenium.webdriver.common.by import By

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.base.movie_entity import Movie, SiteSpecificMovieData, Site
from RatS.filmtipset.filmtipset_site import Filmtipset


class FilmtipsetRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(FilmtipsetRatingsParser, self).__init__(Filmtipset(args), args)
        self.downloaded_file_name = ""
        self.csv_delimiter = ";"

    # TODO remove when filmtipset has cleaned up their "csv" file
    @staticmethod
    def _repair_csv_row(row):
        output = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2}),(.*)(;[\-0-9]*;[1-5])$", row)

        if output is None:
            return row
        escaped_title_value = output.group(2).replace('"', '""')
        repaired_row = f'{output.group(1)};"{escaped_title_value}"{output.group(3)}\n'
        return repaired_row

    @staticmethod
    def _repair_csv_file(filepath):
        copyfile(filepath, filepath + ".bak")
        for line in fileinput.input(filepath, inplace=True):
            print(FilmtipsetRatingsParser._repair_csv_row(line), end="")

    def _file_was_downloaded(self):
        pattern = self.exports_folder + "/ft_betyg_2[0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9].csv"
        files = glob.glob(pattern)
        for filename in files:
            self.downloaded_file_name = os.path.basename(filename)
            return True
        return False

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        filepath = os.path.join(self.exports_folder, self.csv_filename)
        self._repair_csv_file(filepath)
        self.movies = self._parse_movies_from_csv(filepath)

    def _call_download_url(self):
        input_xpath = '//input[@id="submit-export"]'
        self.site.browser.find_element(By.XPATH, input_xpath).click()

    def _convert_csv_row_to_movie(self, headers, row):
        movie = Movie(title=row[headers.index("MovieTitle")])
        movie.site_data[self.site.site] = SiteSpecificMovieData()
        parsed_rating = int(row[headers.index("Score")])
        movie.site_data[self.site.site].my_rating = parsed_rating * 2
        self._extract_imdb_information(movie, row[headers.index("IMDB")])

        return movie

    @staticmethod
    def _extract_imdb_information(movie: Movie, imdb_id):
        try:
            i = int(imdb_id)
            if i < 1:
                return
        except ValueError:
            return

        formatted_imdb_id = f"tt{int(imdb_id):07d}"
        movie.site_data[Site.IMDB] = SiteSpecificMovieData(
            id=formatted_imdb_id,
            url=f"https://www.imdb.com/title/{formatted_imdb_id}",
        )
