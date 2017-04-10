#!/bin/bash
## adapted from https://gist.github.com/tristandostaler/2f8b28f2bf503db4422a5549e8fed538

mkdir /usr/bin
cd /usr/bin || exit

wget https://github.com/mozilla/geckodriver/releases/download/v0.15.0/geckodriver-v0.15.0-linux64.tar.gz
tar -xvzf geckodriver-v0.15.0-linux64.tar.gz
rm geckodriver-v0.15.0-linux64.tar.gz
chmod +x geckodriver
cp geckodriver wires

export PATH=$PATH:/usr/bin/wires
export PATH=$PATH:/usr/bin/geckodriver
