FROM selenium/standalone-firefox:4.20

ENV PYTHONUNBUFFERED 1

RUN sudo apt-get update \
 && sudo apt-get install -y --no-install-recommends vim python3 python3-pip \
 && sudo rm -rf /var/lib/apt/lists/*

RUN sudo mkdir -p /RatS/RatS
WORKDIR /RatS
COPY ["./pyproject.toml", "./poetry.lock", "./transfer_ratings.py", "/RatS/"]
RUN python3 --version && pip3 --version && sudo pip3 install --no-cache-dir poetry \
    && poetry --version && poetry install
COPY ./RatS /RatS/RatS/
RUN sudo chown -R seluser: .

CMD ["/bin/true"]
