import numpy

class ZoomTransformer(object):

    def __init__(self):
        self.matrix = numpy.identity(3)
        #self.matrix = [[3,0,0],[0,2,0],[0,0,1]]

    def ToViewport(self, point):
        return numpy.resize(numpy.matmul(self.matrix, [point[0], point[1], 1]), 2)

    def FromViewport(self, point):
        return numpy.resize(numpy.matmul(numpy.linalg.inv(self.matrix), [point[0], point[1], 1]), 2)

