<p align="center">
  <img src="https://raw.githubusercontent.com/StegSchreck/RatS/master/RatS/img/RatS.png" width="250px">
</p>

# RatS

[![Build Status](https://travis-ci.org/StegSchreck/RatS.svg?branch=master)](https://travis-ci.org/StegSchreck/RatS)
[![Coverage Status by Coveralls](https://coveralls.io/repos/github/StegSchreck/RatS/badge.svg?branch=master)](https://coveralls.io/github/StegSchreck/RatS?branch=master)
[![Maintainability by CodeClimate](https://api.codeclimate.com/v1/badges/9be495ea69fb62e960cb/maintainability)](https://codeclimate.com/github/StegSchreck/RatS/maintainability)
[![Test Coverage by CodeClimate](https://api.codeclimate.com/v1/badges/9be495ea69fb62e960cb/test_coverage)](https://codeclimate.com/github/StegSchreck/RatS/test_coverage)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c0601ed8ba1a4ba5ac1a205521f00622)](https://www.codacy.com/app/StegSchreck/RatS?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=StegSchreck/RatS&amp;utm_campaign=Badge_Grade)
[![Docker Build Status](https://img.shields.io/docker/build/stegschreck/rats.svg?logo=docker)](https://hub.docker.com/r/stegschreck/rats/builds)
[![Docker Image Size](https://images.microbadger.com/badges/image/stegschreck/rats.svg)](https://microbadger.com/images/stegschreck/rats)
[![License](https://img.shields.io/github/license/StegSchreck/RatS.svg)](https://github.com/StegSchreck/RatS/blob/master/LICENSE)
[![Latest Release](https://img.shields.io/github/release/StegSchreck/AngularCV.svg?logo=github)](https://github.com/StegSchreck/RatS/releases)

This project serves for analyzing, and transfering your ratings from one movie tracking / rating website to another.

The goal of this project is to have a universal tool which can transfer your ratings from any site to another without
the need of any manual steps like configuring an API access or whatever. Just configure your credentials (see steps
below), start the tool and relax.

This also works if your lists are marked as private, as this tool uses a browser to login and get the content.

## How do I use this?

### Natively on the command line

This project is currently still under development. Please be patient, as I'm only working on this every once in a while.

1. Make sure you have Python3, Firefox and Xvfb installed on your system.
    This project is designed to run on Linux.
1. Checkout the project
    `git clone https://github.com/StegSchreck/RatS.git && cd RatS`
1. Install the requirements with pip for Python3
    `pip3 install -r requirements.txt`
1. Install Geckodriver

      * Use your system's package manager (if it contains Geckodriver)
        * Arch Linux: `pacman -S geckodriver`
        * MacOS: `brew install geckodriver`
      * Or execute `sudo ./InstallGeckodriver.sh`.
        For this you will need to have tar, wget and curl installed.

1. Set your credentials

    1. Copy the `credentials.cfg.orig` file to `credentials.cfg` and insert your credentials for the sites you need there
    (without any quotation marks etc.).

        Copying the file will conserve the possibility to do a `git pull` later on without overwriting your credentials.

    1. Alternatively, you can set the credentials via environment variables. For example, if you want to set the 
    credentials for your IMDB and Trakt accounts you would need to set these environment variables:
        ```sh
        export IMDB_USERNAME=abc@def.de
        export IMDB_PASWORD=def
        export TRAKT_USERNAME=abc
        export TRAKT_PASWORD=def
        ```
        It is important to use the variable names completely in uppercase!

    1. The third way is to set the environment variables when running the transfer script, like this:
    `IMDB_USERNAME=abc@def.de IMDB_PASWORD=def TRAKT_USERNAME=abc TRAKT_PASWORD=def python3 transfer_ratings.py --source trakt --destination imdb`

    The credentials in environment variables are overruling the ones in the `credentials.cfg` file.
1. Execute the script with **Python3**
    `python3 transfer_ratings.py --source trakt --destination movielens`

    This will first parse your ratings in Trakt, save them in a JSON file for later use and then try to find those
    movies in Movielens an put your rating there. Notice: This will also overwrite rating you already did set there before.

    This script will take some minutes. Relax. You can follow the progress in console output.

    For more information about how to use the script, you can call
    `python3 transfer_ratings.py --help`
1. At the end, the script will print out how many movies were successfully posted. Afterwards all the movies which
  couldn't be found are printed out, so you can check them manually. The failed movie are also exported to a JSON file,
  so you can easily try them again (see below).

### Inside a Docker container

_Please note: This is currently not working on Windows, but I'm working on that._

1. Create a credentials configuration in your home folder, e.g.: `touch ~/.RatS.cfg`
1. Configure your credentials in the file you just created, e.g.:

    ```
    [Trakt]
    USERNAME = abc
    PASSWORD = def
    ```

    Please see the RatS/credentials.cfg.orig in this repository as a template. Please enter your credentials as they are,
    without any quotation marks.
1. Get the Docker image: `docker pull stegschreck/rats`
1. Run the script: `docker run -it -v ~/.RatS.cfg:/RatS/RatS/credentials.cfg stegschreck/rats python3 transfer_ratings.py --source trakt --destination movielens`

    The `-v ~/.RatS.cfg:/RatS/RatS/credentials.cfg` option will load the credentials file you just created from your
    home directory into the docker container, so that the script can use it.

    You will see the progress in your console. If you want to run this in the background, you can add the option `-d` to
    the docker run command to hide the output.
1. If you want to run the command again, simply run `docker start -ai <container-id>`.
    You can find the container id using `docker ps -a` or by running `docker ps -q -l`, if you haven't started any other
    containers in the meanwhile.
1. After the successful run of the transfer script, you may remove the docker container using `docker rm <container-id>`.

### Command line call parameters

1. the first argument (`--source`) is the site where the ratings are parsed from (see [Available Parsers](#currently-available-parsers))
1. the second argument  (`--destination`) is the site where the ratings should be posted (inserted) to (see [Available Inserters](#currently-available-inserters))

You can also omit the destination argument in order to just save the parsing results to a JSON file. You might insert
the saved results anytime later. (see [below](#trying-again-with-former-export-data))

Furthermore, you can define multiple destinations, e.g. like this:
`python3 transfer_ratings.py --source trakt --destination movielens --destination imdb`
in order to use the same data from the parser in this run for multiple destinations.

#### Currently Available Parsers

* Criticker
* FilmAffinity
* Flixster
* iCheckMovies
  * please configure the conversion value for the like/dislike into a numeric rating yourself in the `credentials.cfg`
* IMDB (with IMDB account)
* Letterboxd
* Listal
* Movielens
* MoviePilot
* Plex (locally hosted server)
* TMDB (The Movie Database)
* Trakt

#### Currently Available Inserters

* Criticker
* FilmAffinity
* Flixster
* iCheckMovies
  * please configure the boundaries for the ratings conversion yourself in the `credentials.cfg`
* IMDB (with IMDB account)
* Letterboxd
* Listal
* Metacritic
* Movielens
* MoviePilot
* Plex (locally hosted server)
* TMDB (The Movie Database)
* Trakt

<p align="center">
  <img src="https://raw.githubusercontent.com/StegSchreck/RatS/master/RatS/img/RatS_Ensemble.png">
</p>

### Trying again with former export data

Depending on what you used in the first run:

#### ... using the command line

You can re-use the data you parsed before, without parsing again. This will help you, if you want to distribute from one
source to multiple destinations. The parser tells you in which file he saved his result, the folder is
`./RatS/exports`. You can use this data by calling the script for example this way:

`python3 transfer_ratings.py --source trakt --destination movielens --file 20170721191143_Trakt.json`

Please notice, that the `--source` argument is still needed in order to identify which data to use from the given file
for the inserter.

Furthermore: This section is meant to be used with the native command line version. Docker containers work differently.

#### ... using Docker

1. After the first run of the Docker container: (assuming you didn't start any other Docker containers in the meanwhile)

   * save the state of the container (including the saved data): ```docker commit <container-id> user/RatS```
   * lookup the JSON file the script saved into the exports folder: `docker run -it user/RatS ls -l RatS/exports/`
     (take the latest JSON file)

1. Run the container again, e.g. with a different destination
  `docker run -it -v ~/.RatS.cfg:/RatS/RatS/credentials.cfg user/RatS python3 transfer_ratings.py --source trakt --destination imdb --file 20170721191143_Trakt.json`

#### Switching between environments

You can copy the exported JSON from/to the Docker container if you like. I don't recommend this if you have no
experience with docker. If you have, you already know what to do here ;)

## Problem shooting

### Script aborts because of Timeouts

It might occasionally happen, that the script runs into errors caused by the page loading too slow. In the past, this
was quite an issue. I now tried to build a mechanism with dynamically increasing timeouts. Therefore, the script sleeps
for one second after failing the first try (effective for multiple problematic locations in the code), waiting two
seconds after the second try failed, and so on. The maximum number of tries is ten. If this is reached, the error gets
re-raised and the script will fail.

### Script aborts with WebDriverException

If you recently updated your Firefox, you might encounter the following exception during the login attempt of the parser:

`selenium.common.exceptions.WebDriverException: Message: Expected [object Undefined] undefined to be a string`

This can be fixed by installing the latest version of [Mozilla's Geckodriver](https://github.com/mozilla/geckodriver)
by running again the _Install Geckodriver_ command mentioned [above](#natively-on-the-command-line).

### Login attempt does not work

This can have multiple explanations. One is, that you are using a password which starts or ends with a space character.
RatS is currently not capable of dealing with that. If your credentials have a space character in the middle though, it
will work fine.

## You are missing a feature or noticed something is wrong?

Before submitting a bug ticket, I would ask you to check first whether all dependencies are up-to-date, especially `geckodriver`.

Please [write a ticket](https://github.com/StegSchreck/RatS/issues/new/choose), I will have a look as soon as I can.

## Where does the name come from?

The name for this project comes from the first letters of "**rat**ing **s**ynchronisation". It is that simple. It is also
a reference to the movie "Departed".
