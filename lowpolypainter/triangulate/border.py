# Python Modules
import math
import numpy as np
from scipy.spatial import ConvexHull

"""
Border Class

Description:
Creates border points and generates convex hull from current mesh.
Border points are generated with step size.
"""
class Border(object):

    def __init__(self, width, height):
        self.hull = []
        self.points = []
        self.width = width
        self.height = height
        self.corner = [0,0,0,0]

    def generateCorners(self):
        self.points = [[0,0],
                       [self.width-1,0],
                       [self.width-1,self.height-1],
                       [0,self.height-1]]

    def generatePoints(self, step):
        width = self.width
        height = self.height

        # Height
        height_indices = np.arange(0, height, math.floor(height/step), dtype=int)
        height_indices[-1] = height - 1
        height_points_west = np.zeros((len(height_indices), 2), dtype=int)
        height_points_east = np.zeros((len(height_indices), 2), dtype=int)
        for i in range(len(height_points_west)):
            height_points_west[i][1] = height_indices[i]
            height_points_east[i] = [width - 1, height_indices[i]]

        # Width
        width_indices = np.arange(0, width, math.floor(width/step), dtype=int)
        width_indices[-1] = width - 1
        width_points_north = np.zeros((len(width_indices), 2), dtype=int)
        width_points_south = np.zeros((len(width_indices), 2), dtype=int)
        for i in range(len(width_points_north)):
            width_points_north[i][0] = width_indices[i]
            width_points_south[i] = [width_indices[i], height - 1]

        self.points = np.concatenate([width_points_north,
                                      height_points_east,
                                      width_points_south[::-1],
                                      height_points_west[::-1]])

    def generateConvexHull(self, verts):
        if len(verts) < 4:
            return

        hull = ConvexHull(verts)
        for index in hull.vertices:
            self.hull.append(verts[index])

        self.generateCorners()
        for i1 in range(len(self.points)):
            p1 = self.points[i1]
            minDist = float('Inf')
            for i2 in range(len(self.hull)):
                p2 = self.hull[i2]
                dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

                if dist < minDist:
                    minDist = dist
                    self.corner[i1] = i2
