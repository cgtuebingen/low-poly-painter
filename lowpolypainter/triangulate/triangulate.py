# Python Modules
import cv2
import math
import numpy as np
from PIL import ImageTk, Image
from random import randint
from skimage import feature
from skimage.color import rgb2gray
from scipy.spatial import Delaunay

"""
Triangulate Class

Description:
Creates mesh from image with canny edges.
"""
class Triangulate(object):

    def __init__(self, inputimage, points):
        self.oldPoints = points
        if isinstance(inputimage, basestring):
            filepath = 'lowpolypainter/resources/images/'
            self.image = cv2.imread(filepath + inputimage, 0)
        else:
            img_arr = np.array(inputimage, dtype=np.uint8)
            img_gray = rgb2gray(img_arr)
            self.image = img_gray
        self.points = np.array([], dtype=int).reshape(0,2)

    def generateRandom(self, size):
        if size == 0:
            return
        height, width = self.image.shape[:2]
        random_points = np.zeros((size, 2), dtype=int)
        for i in range(size):
            random_points[i] = [randint(0, width - 1), randint(0, height - 1)]
        self.points = np.vstack([self.points, random_points])

    def generateCanny(self, sigma=0, mask=None):
        mask = np.transpose(mask)
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
        return Delaunay(self.points).simplices if len(self.points) != 0 else []
