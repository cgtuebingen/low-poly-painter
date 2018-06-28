from __future__ import division

# Python Modules
import numpy as np
import math as math

"""
Color Class

Description:
Generates color for faces and returns HEX string.
"""

class Color:
    def __init__(self, array, percentageX, percentageY):
        self.imageArray = array
        self.height = len(self.imageArray)
        self.width = len(self.imageArray[0])
        self.flattenImageArray = array.ravel()
        self.stepX = int(math.pow(percentageX, -1))
        self.stepY = int(math.pow(percentageY, -1))

    # Generates random color
    def random(self):
        r = '%02x'%np.random.randint(255)
        g = '%02x'%np.random.randint(255)
        b = '%02x'%np.random.randint(255)
        return '#' + r + g + b

    # Generates color from vertices
    def fromPoints(self, vertices):

        r, g, b = 0, 0, 0
        length = len(vertices)

        # Get pixel value from vertex
        for i in range(length):
            x = vertices[i][0]
            y = vertices[i][1]
            count = 3 * (y * self.height + x)
            r += self.flattenImageArray[count]
            g += self.flattenImageArray[count + 1]
            b += self.flattenImageArray[count + 2]

        # RGB HEX string
        rs = '%02x'%int(r / length)
        gs = '%02x'%int(g / length)
        bs = '%02x'%int(b / length)

        return '#' + rs + gs + bs

    # Generates color from image
    # (!) Vertices must have anticlockwise order
    def fromImage(self, vertices):
        # Vertices x and y
        v1x, v2x, v3x = vertices[0][0], vertices[1][0], vertices[2][0]
        v1y, v2y, v3y = vertices[0][1], vertices[1][1], vertices[2][1]

        # Calculate slope for each edge
        mv2v1 = (v2x - v1x) / (v2y - v1y) if (v2y - v1y) != 0 else 0
        mv3v1 = (v3x - v1x) / (v3y - v1y) if (v3y - v1y) != 0 else 0
        mv3v2 = (v3x - v2x) / (v3y - v2y) if (v3y - v2y) != 0 else 0

        # RGB values and pixel counter
        r, g, b = 0, 0, 0
        pcounter = 0

        ymin = v1y
        ymax = v2y if v2y > v3y else v3y

        # Get every pixel from ymin to ymax
        for row in range(ymin, ymax, self.stepY):
            if row >= v2y:
                xmin = int(mv3v2 * (row - v3y)) + v3x - 1
                xmax = int(mv3v1 * (row - v3y)) + v3x
            elif row >= v3y:
                xmin = int(mv2v1 * (row - v2y)) + v2x - 1
                xmax = int(mv3v2 * (row - v3y)) + v3x
            else:
                xmin = int(mv2v1 * (row - v2y)) + v2x - 1
                xmax = int(mv3v1 * (row - v3y)) + v3x

            # Get every pixel from xmin to xmax
            for col in range(xmin, xmax, self.stepX):
                count = 3 * (row * self.height + col)
                r += self.flattenImageArray[count]
                g += self.flattenImageArray[count + 1]
                b += self.flattenImageArray[count + 2]
                pcounter += 1

        # Triangle created without area
        # Generate color from vertices
        if pcounter != 0:
            # RGB HEX string
            rs = '%02x'%(r / pcounter)
            gs = '%02x'%(g / pcounter)
            bs = '%02x'%(b / pcounter)
            return '#' + rs + gs + bs
        else:
            return self.fromPoints(vertices)
