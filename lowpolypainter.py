#!/usr/bin/env python2

# Python Modules
import sys
import ctypes

# Local Modules
from lowpolypainter.window import Window

# TODO: Add module getopt for better argv managment
# TODO: Maybe add outputimage

"""
Main File

Description:
Loads arguments from command line and starts up application.
Goto /lowpolypainter/window.py to start programming
"""

def main(argv):
    # Windows high res support?
    if 'win' == sys.platform:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    if len(argv) != 1:
        print 'test.py <inputimage>'
        sys.exit(2)
    else:
        inputimage = argv[0]
        window = Window(inputimage)
        window.loadMeshData()
        window.root.mainloop()

if __name__ == "__main__":
    main(sys.argv[1:])
