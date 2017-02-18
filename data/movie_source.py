class MovieSource:
    def __init__(self):
        self.id = ''
        self.url = ''
        self.my_rating = ''
        self.overall_rating = ''

    def __str__(self):
        return "[%s] URL:%s ME:%s OVERALL:%s" % \
               (self.id, self.url, self.my_rating, self.overall_rating)

    def to_json(self):
        json = {
            'id': self.id,
            'url': self.url,
            'my_rating': self.my_rating,
            'overall_rating': self.overall_rating
        }
        return json

    @staticmethod
    def from_json(json):
        movie_source = MovieSource()
        movie_source.id = json['id']
        movie_source.url = json['url']
        movie_source.my_rating = json['my_rating']
        movie_source.overall_rating = json['overall_rating']
        return movie_source
