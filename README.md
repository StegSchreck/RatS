<p align="center">
  <img src="https://github.com/StegSchreck/RatS/blob/master/RatS/img/RatS.png" width="250px">
</p>

# RatS

[![Build Status](https://travis-ci.org/StegSchreck/RatS.svg?branch=master)](https://travis-ci.org/StegSchreck/RatS)
[![Coverage Status](https://coveralls.io/repos/github/StegSchreck/RatS/badge.svg?branch=master)](https://coveralls.io/github/StegSchreck/RatS?branch=master)
[![Code Climate](https://codeclimate.com/github/StegSchreck/RatS/badges/gpa.svg)](https://codeclimate.com/github/StegSchreck/RatS)

This project serves for parsing your ratings from one movie tracking / rating website to another.

The goal of this project is to have a universal tool which can transfer your ratings from any site to another without 
the need of any manual steps like configuring an API access or whatever. 
Just configure you credentials (see steps below), start the tool and relax.

This also works if your lists are marked as private, as this tool uses a browser to login and get the content.

## How do I use this?

This project is currently still under development. Please be patient, as I'm only working on this every once in a while.

1. Checkout the project
    `git clone https://github.com/StegSchreck/RatS.git && cd RatS`
1. Install the requirements
    `pip install -r requirements.txt`
1. Install Geckodriver
    `sudo ./InstallGeckodriver.sh`
1. Copy the `credentials.cfg.orig` file to `credentials.cfg` and insert your credentials for the sites there.
1. Execute the script
    `python transfer_ratings.py trakt movielens`

    This will first parse your ratings in Trakt, save them in a JSON file for later use and then try to find those movies in Movielens an put your rating there. Notice: This will also overwrite rating you already did set there before.

    This script will take some minutes. Relax. You can follow the progress in console output.
1. At the end, the script will print out how many movies were successfully posted. Afterwards all the movies which couldn't be found are printed out, so you can check them manually. The failed movie are also exported to a JSON file, so you can easily try them again (see below).

### Command line call parameters

1. the first argument is the site where the ratings are parsed from (see [Available Parsers](#parsers))
1. the second argument is the site where the ratings should be posted (inserted) to (see [Available Inserters](#inserters))

<a name="parsers"></a>

#### Currently Available Parsers

* Criticker
* IMDB (with IMDB account)
* Letterboxd
* Listal
* Movielens
* TMDB (The Movie Database)
* Trakt

<a name="inserters"></a>

#### Currently Available Inserters

* Criticker
* Flixster
* IMDB (with IMDB account)
* Letterboxd
* Listal
* Movielens
* TMDB (The Movie Database)
* Trakt

### Trying again with former export data

You can use the data you parsed before again without parsing again. The parser tells you in which file he saved his results, the folder is `./RatS/exports`. You can use this data by commenting out the parsing in the `transfer_ratings.py` script and comment in the file loader part, where you just have to adjust the filename.

## Problem shooting

### Script aborts because of Timeouts

It might occasionally happen, that the script runs into errors caused by the page loading too slow. I tried to build some timeouts in for these cases. But depending on your internet connection speed etc. you might still run into this, especially when interacting with Movielens. The only advice I can give you for now is to increase the time.sleep() in the scripts. I will try to come up with a better solution in the future.

### Script aborts with WebDriverException

If you recently updated your Firefox, you might encounter the following exception during the login attempt of the parser:

`selenium.common.exceptions.WebDriverException: Message: Expected [object Undefined] undefined to be a string`

This can be fixed by installing the latest version of [Mozilla's Geckodriver](https://github.com/mozilla/geckodriver) by running again the following command:
    `sudo ./InstallGeckodriver.sh`


## You are missing a feature or noticed something is wrong?

Please [write a ticket](https://github.com/StegSchreck/RatS/issues/new), I will have a look as soon as I can.

## Where does the name come from?

The name for this project comes from the first letters of "**rat**ing **s**ynchronisation". It's that simple.
