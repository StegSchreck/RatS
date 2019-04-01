FROM selenium/standalone-firefox

MAINTAINER Sebastian Schreck <sebastian.schreck@stegschreck.de>

RUN sudo apt-get update && sudo apt-get install -y vim python3 python3-pip

ENV PYTHONUNBUFFERED 1

RUN sudo mkdir /RatS
COPY . /RatS
WORKDIR /RatS
RUN sudo chown -R seluser: .
RUN sudo pip3 install --no-cache-dir -r ./requirements.txt

CMD ["/bin/true"]
