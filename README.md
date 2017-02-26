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
   
## Problem shooting
### Script aborts because of Timeouts
It might occassionally happen, that the script runs into errors caused by the page loading too slow. I tried to build some timeouts in for these cases. But depending on your internet connection speed etc. you might still run into this, especially when interacting with Movielense. The only advice I can give you for now is to increase the timeouts in the scripts. I will try to come up with a better solution in the future.

## Where does the name come from?
The name for this project comes from the first letters of "**rat**ing **s**ynchronisation". It's that simple.
