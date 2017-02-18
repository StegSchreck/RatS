from RatS.inserters.base_inserter import Inserter
from RatS.sites.movielense import Movielense


class MovielenseInserter(Inserter):
    def __init__(self):
        super(MovielenseInserter, self).__init__(Movielense())
