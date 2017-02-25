<p align="center">
  <img src="https://github.com/StegSchreck/RatS/blob/master/RatS/img/RatS.png" width="250px">
</p>

# RatS [![Build Status](https://travis-ci.org/StegSchreck/RatS.svg?branch=master)](https://travis-ci.org/StegSchreck/RatS) [![Coverage Status](https://coveralls.io/repos/github/StegSchreck/RatS/badge.svg?branch=master)](https://coveralls.io/github/StegSchreck/RatS?branch=master)

This project serves for parsing your ratings from one movie tracking / rating website to another.

## How do I use this?
This project is currently still under development. Please be patient, as I'm only working on this every once in a while.

1. Checkout the project
    `git clone https://github.com/StegSchreck/RatS.git && cd RatS`
2. Install the requirements
    `pip install -r requirements.txt`
3. Execute the script
    `python get_trakt_ratings_to_movielense.py`
    
    This will first parse your ratings in Trakt, save them in a JSON file for later use and then try to find those movies in Movielense an put your rating there.
    
    This will take some minutes. Relax. You can follow the progress in console output.

## Where does the name come from?
The name for this project comes from the first letters of "**rat**ing **s**ynchronisation". It's that simple.
