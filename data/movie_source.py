class MovieSource:
    def __str__(self):
        return "[%s] URL:%s ME:%s OVERALL:%s" % \
               (self.id, self.url, self.my_rating, self.overall_rating)

    id = ''
    url = ''
    my_rating = ''
    overall_rating = ''
