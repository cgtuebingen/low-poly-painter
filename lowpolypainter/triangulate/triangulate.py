# Python Modules
import cv2
import math
import numpy as np
from random import randint
from skimage import feature
from scipy.spatial import Delaunay

"""
Triangulate Class

Description:
Creates mesh from image with canny edges.
"""
class Triangulate(object):

    def __init__(self, inputimage, points):
        self.oldPoints = points
        filepath = 'lowpolypainter/resources/images/'
        self.image = cv2.imread(filepath + inputimage, 0)
        self.points = np.array([], dtype=int).reshape(0,2)

    def generateCorners(self, step):
        height, width = self.image.shape[:2]

        # Height
        height_indices = np.arange(0, height, math.floor(height/step), dtype=int)
        height_indices[-1] = height - 1
        height_points_west = np.zeros((len(height_indices), 2), dtype=int)
        height_points_east = np.zeros((len(height_indices), 2), dtype=int)
        for i in range(len(height_points_west)):
            height_points_west[i][1] = height_indices[i]
            height_points_east[i] = [width - 1, height_indices[i]]
        self.points = np.vstack([self.points, height_points_west])
        self.points = np.vstack([self.points, height_points_east])

        # Width
        width_indices = np.arange(0, width, math.floor(width/step), dtype=int)
        width_indices[-1] = width - 1
        width_points_north = np.zeros((len(width_indices), 2), dtype=int)
        width_points_south = np.zeros((len(width_indices), 2), dtype=int)
        for i in range(len(width_points_north)):
            width_points_north[i][0] = width_indices[i]
            width_points_south[i] = [width_indices[i], height - 1]
        self.points = np.vstack([self.points, width_points_north])
        self.points = np.vstack([self.points, width_points_south])

    def generateRandom(self, size):
        if size == 0:
            return
        height, width = self.image.shape[:2]
        random_points = np.zeros((size, 2), dtype=int)
        for i in range(size):
            random_points[i] = [randint(0, width - 1), randint(0, height - 1)]
        self.points = np.vstack([self.points, random_points])

    def generateCanny(self, sigma=0, mask=None):
        cannyPoints = feature.canny(self.image, sigma=sigma, mask=mask)
        cannyPointsIndices = np.nonzero(cannyPoints)
        cannyPointsCombined = np.vstack((cannyPointsIndices[1],
                                         cannyPointsIndices[0])).T
        self.points = np.vstack((self.points, cannyPointsCombined))

    def subsetCanny(self, size):
        indices = np.arange(len(self.points))
        np.random.shuffle(indices)
        cropped_indices = indices[:size]
        self.points = self.points[cropped_indices]

    def triangulate(self, size=1000, random=50):
        self.subsetCanny(size)
        self.generateRandom(random)
        if len(self.oldPoints) != 0:
            self.points = np.vstack([self.points, self.oldPoints])
        return Delaunay(self.points).simplices
