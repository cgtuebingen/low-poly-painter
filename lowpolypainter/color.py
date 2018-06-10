# Python Modules
import numpy as np
import math as math
from PIL import Image

# TODO: Set percentage of pixels for fromImage

"""
Color Class

Description:
Generates color for faces and returns HEX string.
"""

class Color:
    @staticmethod
    # Generates random color
    def random():
        r = '%02x'%np.random.randint(255)
        g = '%02x'%np.random.randint(255)
        b = '%02x'%np.random.randint(255)
        return '#' + r + g + b

    @staticmethod
    # Generates color from image
    # With percentage of pixels 0 < x <= 1
    # (!) Vertices must have anticlockwise order
    def fromImage(image, percentage, vertices):

        # Load image into array
        imageArray = np.array(image)

        # Vertex1 x and y
        v1x = vertices[0][0]
        v1y = vertices[0][1]

        # Vertex2 x and y
        v2x = vertices[1][0]
        v2y = vertices[1][1]

        # Vertex3 x and y
        v3x = vertices[2][0]
        v3y = vertices[2][1]

        # Find max and min values of triangle
        xmin = v2x
        xmax = v3x
        ymin = v1y
        ymax = v2y if v2y > v3y else v3y

        # Calculate slope for each edge
        mv2v1 = (v2x - v1x) / float(v2y - v1y) if (v2y - v1y) != 0 else 0
        mv3v1 = (v3x - v1x) / float(v3y - v1y) if (v3y - v1y) != 0 else 0
        mv3v2 = (v3x - v2x) / float(v3y - v2y) if (v3y - v2y) != 0 else 0

        # Stores value and number of pixels in triangle
        pixelArray = np.zeros(3)
        pixelCounter = 0

        # Get every pixel from ymin to ymax
        for row in range(ymin, ymax):
            # Calculate col range for each row
            if row >= v2y:
                xmin = int(mv3v2 * (row - v3y)) + v3x
                xmax = int(mv3v1 * (row - v3y)) + v3x
            elif row >= v3y:
                xmin = int(mv2v1 * (row - v2y)) + v2x
                xmax = int(mv3v2 * (row - v3y)) + v3x
            else:
                xmin = int(mv2v1 * (row - v2y)) + v2x
                xmax = int(mv3v1 * (row - v3y)) + v3x

            # Set step size with percentage
            stepSize = int(math.pow(percentage, -1))

            # Get every pixel from xmin to xmax
            for col in range(xmin, xmax, stepSize):
                pixelArray = pixelArray + imageArray[row][col]
                pixelCounter += 1

        # TODO: Remove this just for debugging
        # Triangle created without area
        if pixelCounter == 0:
            return '#FFFFFF'

        # Calculate average pixel value
        pixelArray = np.divide(pixelArray, pixelCounter)

        # Create RGB HEX string
        r = '%02x'%int(pixelArray[0])
        g = '%02x'%int(pixelArray[1])
        b = '%02x'%int(pixelArray[2])

        return '#' + r + g + b
