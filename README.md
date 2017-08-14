<p align="center">
  <img src="https://github.com/StegSchreck/RatS/blob/master/RatS/img/RatS.png" width="250px">
</p>

# RatS

[![Build Status](https://travis-ci.org/StegSchreck/RatS.svg?branch=master)](https://travis-ci.org/StegSchreck/RatS)
[![Coverage Status](https://coveralls.io/repos/github/StegSchreck/RatS/badge.svg?branch=master)](https://coveralls.io/github/StegSchreck/RatS?branch=master)
[![Code Climate](https://codeclimate.com/github/StegSchreck/RatS/badges/gpa.svg)](https://codeclimate.com/github/StegSchreck/RatS)
[![Docker image](https://images.microbadger.com/badges/image/stegschreck/rats.svg)](https://microbadger.com/images/stegschreck/rats)

This project serves for parsing your ratings from one movie tracking / rating website to another.

The goal of this project is to have a universal tool which can transfer your ratings from any site to another without 
the need of any manual steps like configuring an API access or whatever. 
Just configure you credentials (see steps below), start the tool and relax.

This also works if your lists are marked as private, as this tool uses a browser to login and get the content.

## How do I use this?

### Natively on the command line

This project is currently still under development. Please be patient, as I'm only working on this every once in a while.

1. Make sure you have Python3 and Xvfb installed on your system.
    This project is designed to run on Linux.
1. Checkout the project
    `git clone https://github.com/StegSchreck/RatS.git && cd RatS`
1. Install the requirements
    `pip install -r requirements.txt`
1. Install Geckodriver 

    **Linux:** `sudo ./InstallGeckodriver.sh`, for this you will need to have tar and wget installed.
    
    **MAC:** `brew install geckodriver`
1. Copy the `credentials.cfg.orig` file to `credentials.cfg` and insert your credentials for the sites there.
1. Execute the script with **Python3**
    `python3 transfer_ratings.py --source trakt --destination movielens`

    This will first parse your ratings in Trakt, save them in a JSON file for later use and then try to find those movies in Movielens an put your rating there. Notice: This will also overwrite rating you already did set there before.

    This script will take some minutes. Relax. You can follow the progress in console output.
    
    For more information about how to use the script, you can call 
    `python3 transfer_ratings.py --help`
1. At the end, the script will print out how many movies were successfully posted. Afterwards all the movies which couldn't be found are printed out, so you can check them manually. The failed movie are also exported to a JSON file, so you can easily try them again (see below).

### Inside a Docker container

1. Create a credentials configuration in your home folder, e.g.: `touch ~/.RatS.cfg`
1. Configure your credentials in the file you just created, e.g.:
    ```
    [Trakt]
    USERNAME = abc
    PASSWORD = def
    ```
    Please see the RatS/credentials.cfg.orig in this repository as a template.
1. Get the Docker image: `docker pull stegschreck/rats`
1. Run the script: `docker run -it -v ~/.RatS.cfg:/RatS/RatS/credentials.cfg stegschreck/rats python3 transfer_ratings.py --source trakt --destination movielens`
    
    The `-v ~/.RatS.cfg:/RatS/RatS/credentials.cfg` option will load the credentials file you just created from your home directory into the docker container, so that the script can use it.
    
    You will see the progress in your console. If you want to run this in the background, you can add the option `-d` to the docker run command to hide the output.
1. If you want to run the command again, simply run `docker start -ai <container-id>`.
    You can find the container id using `docker ps -a` or by running `docker ps -q -l`, if you haven't started any other containers in the meanwhile.
1. After the successful run of the transfer script, you may remove the docker container using `docker rm <container-id>`. 

### Command line call parameters

1. the first argument (`--source`) is the site where the ratings are parsed from (see [Available Parsers](#parsers))
1. the second argument  (`--destination`) is the site where the ratings should be posted (inserted) to (see [Available Inserters](#inserters))

You can also omit the destination argument in order to just save the parsing results to a JSON file. You might insert the saved results anytime later. (see [below](#retry))

<a name="parsers"></a>

#### Currently Available Parsers

* Criticker
* Flixster
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
* iCheckMovies
  * please configure the boundaries for the ratings conversion yourself in the credentials.cfg
* IMDB (with IMDB account)
* Letterboxd
* Listal
* Metacritic
* Movielens
* TMDB (The Movie Database)
* Trakt

<a name="retry"></a>

### Trying again with former export data

Depending on what you used in the first run:

#### ... using the command line

You can re-use the data you parsed before, without parsing again. This will help you, if you want to distribute from one source to multiple destinations. The parser tells you in which file he saved his results, the folder is `./RatS/exports`. You can use this data by calling the script for example this way:

`python3 transfer_ratings.py --source trakt --destination movielens --file 20170721191143_Trakt.json`

Please notice, that the `--source` argument is still needed in order to identify which data to use from the file for the inserter.

Furthermore: This section is meant to be used with the native command line version. Docker containers work differently.

#### ... using Docker

1. After the first run of the Docker container: (assuming you didn't start any other Docker containers in the meanwhile)
   * save the state of the container (including the saved data): ```docker commit <container-id> user/RatS```
   * lookup the JSON file the script saved into the exports folder: `docker run -it user/RatS ls -l RatS/exports/` (take the latest JSON file)
1. Run the container again, e.g. with a different destination 
  `docker run -it -v ~/.RatS.cfg:/RatS/RatS/credentials.cfg user/RatS python3 transfer_ratings.py --source trakt --destination imdb --file 20170721191143_Trakt.json`
  
#### Switching between environments
You can copy the exported JSON from/to the Docker container if you like. I don't recommend this if you have no experience with docker. If you have, you already know what to do here ;)

## Problem shooting

### Script aborts because of Timeouts

It might occasionally happen, that the script runs into errors caused by the page loading too slow. I tried to build some timeouts in for these cases. But depending on your internet connection speed etc. you might still run into this, especially when interacting with Movielens. The only advice I can give you for now is to increase the time.sleep() in the scripts. I will try to come up with a better solution in the future.

### Script aborts with WebDriverException

If you recently updated your Firefox, you might encounter the following exception during the login attempt of the parser:

`selenium.common.exceptions.WebDriverException: Message: Expected [object Undefined] undefined to be a string`

This can be fixed by installing the latest version of [Mozilla's Geckodriver](https://github.com/mozilla/geckodriver) by running again the command mentioned above.


## You are missing a feature or noticed something is wrong?

Please [write a ticket](https://github.com/StegSchreck/RatS/issues/new), I will have a look as soon as I can.

## Where does the name come from?

The name for this project comes from the first letters of "**rat**ing **s**ynchronisation". It's that simple.
