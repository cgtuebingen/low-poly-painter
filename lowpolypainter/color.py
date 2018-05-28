# Python Modules
import numpy as np
from PIL import Image

# TODO: Generate color with image array

"""
Color Class

Description:
Generates color for faces and return HEX string.
"""


class Color:
    @staticmethod
    def random():
        r = '%02x'%np.random.randint(255)
        g = '%02x'%np.random.randint(255)
        b = '%02x'%np.random.randint(255)
        return '#' + r + g + b

    @staticmethod
    def fromImage(image, faceVerticies):
        # print image

        r = '%02x'%np.random.randint(255)
        g = '%02x'%np.random.randint(255)
        b = '%02x'%np.random.randint(255)
        return '#' + r + g + b
