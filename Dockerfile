FROM selenium/standalone-firefox

MAINTAINER Sebastian Schreck <github@stegschreck.de>

ENV PYTHONUNBUFFERED 1

RUN sudo apt-get update \
 && sudo apt-get install -y --no-install-recommends vim python3 python3-pip \
 && sudo rm -rf /var/lib/apt/lists/*

RUN sudo mkdir /RatS
COPY . /RatS
WORKDIR /RatS
RUN sudo chown -R seluser: .
RUN sudo pip3 install --no-cache-dir setuptools \
 && sudo pip3 install --no-cache-dir -r ./requirements.txt

CMD ["/bin/true"]
