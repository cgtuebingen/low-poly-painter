import numpy
from numpy.linalg import inv

class ZoomTransformer(object):

    def __init__(self):
        self.matrix = numpy.identity(3)

    def ToViewport(self, point):
        ret = numpy.matmul(self.matrix, [point[0], point[1], 1])
        ret.resize(2)
        return ret
