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
        self.sites = []
        self.points = []
        self.sites_orientation = []
        self.width = width
        self.height = height

    """ Generate Points """
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

    """ Generate Convex Hull """
    def generateConvexHull(self, verts):
        # hull points
        hull_points = []
        hull = ConvexHull(verts)
        for index in hull.vertices:
            hull_points.append(verts[index])

        # corner points
        h, w = self.height - 1, self.width - 1
        corner_points = [[0,0],[w,0],[w,h],[0,h]]

        # corner hull points
        corner_hull_points_idx = [0, 0, 0, 0]
        for i1 in range(len(corner_points)):
            p1 = corner_points[i1]
            minDist = float('Inf')
            for i2 in range(len(hull_points)):
                p2 = hull_points[i2]
                dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                if dist < minDist:
                    minDist = dist
                    corner_hull_points_idx[i1] = i2

        # sites of hull points
        corner_hull_points_idx_sorted = np.argsort(corner_hull_points_idx)
        chpi, chpis = corner_hull_points_idx, corner_hull_points_idx_sorted
        half2_site1 = hull_points[0:chpi[chpis[0]]+1]
        half1_site1 = hull_points[chpi[chpis[3]]:len(hull_points)]
        site1 = half1_site1 + half2_site1
        site2 = hull_points[chpi[chpis[0]]:chpi[chpis[1]]+1]
        site3 = hull_points[chpi[chpis[1]]:chpi[chpis[2]]+1]
        site4 = hull_points[chpi[chpis[2]]:chpi[chpis[3]]+1]
        self.sites = [site1, site2, site3, site4]

        # sites orientation
        sites_orientation_calculate = [[1,0,0,0],[0,1,w,0],[1,0,0,h],[0,1,0,0]]
        socs = np.asarray(sites_orientation_calculate)[chpis].tolist()

        for site_idx in range(len(self.sites)):
            site_idx_lowered = (site_idx - 1) % len(self.sites)
            site = [corner_points[chpis[site_idx_lowered]]]
            for point in self.sites[site_idx][1:-1]:
                x = socs[site_idx_lowered][0]*point[0]+socs[site_idx_lowered][2]
                y = socs[site_idx_lowered][1]*point[1]+socs[site_idx_lowered][3]
                site.append([x,y])
            site.append(corner_points[chpis[(site_idx) % len(self.sites)]])
            self.sites_orientation.append(site)
