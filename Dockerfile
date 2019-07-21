FROM selenium/standalone-firefox

ENV PYTHONUNBUFFERED 1

RUN sudo apt-get update \
 && sudo apt-get install -y --no-install-recommends vim python3 python3-pip \
 && sudo rm -rf /var/lib/apt/lists/*

RUN sudo mkdir -p /RatS/RatS
WORKDIR /RatS
COPY ["./requirements.txt", "./transfer_ratings.py", "/RatS/"]
RUN sudo pip3 install --no-cache-dir setuptools \
 && sudo pip3 install --no-cache-dir -r ./requirements.txt
COPY ./RatS /RatS/RatS/
RUN sudo chown -R seluser: .

CMD ["/bin/true"]
