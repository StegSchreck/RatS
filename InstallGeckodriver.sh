#!/bin/bash
## adapted from https://gist.github.com/tristandostaler/2f8b28f2bf503db4422a5549e8fed538

mkdir /usr/bin
cd /usr/bin || exit

LATEST_RELEASE=$(curl -L -s -H 'Accept: application/json' https://github.com/mozilla/geckodriver/releases/latest)
LATEST_VERSION=$(echo ${LATEST_RELEASE} | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')

wget https://github.com/mozilla/geckodriver/releases/download/${LATEST_VERSION}/geckodriver-${LATEST_VERSION}-linux64.tar.gz || exit
tar -xvzf geckodriver-${LATEST_VERSION}-linux64.tar.gz
rm geckodriver-${LATEST_VERSION}-linux64.tar.gz
chmod +x geckodriver
cp geckodriver wires

export PATH=$PATH:/usr/bin/wires
export PATH=$PATH:/usr/bin/geckodriver
