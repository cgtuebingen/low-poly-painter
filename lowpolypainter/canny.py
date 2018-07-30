# Python Modules
import cv2
import numpy as np
from scipy.spatial import Delaunay

# TODO: Checkout kirsch operator and sobel filter

"""
Canny Class

Description:
Creates mesh from image with canny edges.
"""
class Canny(object):

    def __init__(self, inputimage):
        # Load image
        filepath = 'lowpolypainter/resources/images/' + inputimage
        self.image = cv2.imread(filepath, 0)

        # Points on picture which are features
        self.points = np.array([], dtype=int).reshape(0,2)

    def generateCorners(self):
        # Added corners serve for better look
        # TODO: Add points on image edges
        height, width = self.image.shape[:2]
        self.points = np.vstack([self.points,
                                [[0,0],[0,height],[width,0],[width,height]]])

    def generateCanny(self, treshhold1, treshhold2):
        # Generate canny points
        cannyPoints = cv2.Canny(self.image, treshhold1, treshhold2)
        cannyPointsIndices = np.nonzero(cannyPoints)
        cannyPointsCombined = np.vstack((cannyPointsIndices[1],
                                         cannyPointsIndices[0])).T
        #print len(cannyPointsCombined)
        #percentage = int(len(cannyPointsCombined) * 0.2)
        #cannyPointsCombined = cannyPointsCombined[np.random.choice(cannyPointsCombined.shape[0], percentage, replace=False), :]
        self.points = np.vstack((self.points, cannyPointsCombined))


    def generateDelaunay(self):
        #print len(Delaunay(self.points).simplices)
        return Delaunay(self.points).simplices

        # counter = 0
        # for row in range(len(points)):
        #     for col in range(len(points[row])):
        #         if points[row][col] == 255:
        #             counter = counter + 1
        #             if counter > 5:
        #                 counter = 0
        #                 self.mesh.addVertex(col,row)
        #                 array = np.vstack([array, [col,row]])
        #
        # tri = Delaunay(array)
        # for s in tri.simplices:
        #     self.mesh.addFace(s[0],s[1],s[2], '#FFFFFF')
