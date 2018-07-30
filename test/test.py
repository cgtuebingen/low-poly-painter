#!/usr/bin/env python2

# Python Modules
import sys
import cv2
from matplotlib import pyplot as plt


"""
Test File

Description:
Loads arguments from command line and shows canny points.
"""

def main(argv):
    if len(argv) != 1:
        print 'test.py <inputimage>'
        sys.exit(2)
    else:
        inputimage = argv[0]
        filepath = 'lowpolypainter/resources/images/' + inputimage
        image = cv2.imread(filepath, 0)
        points = cv2.Canny(image, 100, 200)

        plt.subplot(121),plt.imshow(image, cmap = 'gray')
        plt.title('Original Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.imshow(points,cmap = 'gray')
        plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

        plt.show()

if __name__ == "__main__":
    main(sys.argv[1:])
