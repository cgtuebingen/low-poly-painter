# Python Modules
import svgwrite
from Tkinter import *
import tkFileDialog
import os, errno


def exportDialog(mesh, width, height):
    defaultDirectory = './graphics/'

    try:
        os.makedirs(defaultDirectory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    filename = tkFileDialog.asksaveasfilename(initialdir = defaultDirectory,title = "Select file",filetypes = (("svg files","*.svg"),("all files","*.*")))
    exportFromCanvasObjectsMesh(filename, mesh, width, height)


def exportFromCanvasObjectsMesh(filename, mesh, width, height):
    if '.' in filename:
        filename = filename.split('.')[0]
    img = svgwrite.Drawing(filename + '.svg', size=(str(width), str(height)))
    for face in mesh.faces:
        # vertices for triangle
        points = face.getCoordinates(face.getVerticesCoords())
        # color of the face, converted to decimal rgb values
        color = svgwrite.rgb(r=int(face.color[1:3], 16),
                             g=int(face.color[3:5], 16),
                             b=int(face.color[5:7], 16),
                             mode='RGB')
        # add triangle to image
        # HACK: Twice to get less gaps in the final svg
        img.add(img.polygon(points=points, fill=color))
        img.add(img.polygon(points=points, fill=color))
    # save image
    img.save()
