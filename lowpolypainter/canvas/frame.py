# Python Modules
import time
import math
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image

# Local Modules
from mesh import Mesh
from lowpolypainter.color import Color
from lowpolypainter.triangulate.triangulate import Triangulate

# Masks
CTRL_MASK = 0x0004

class CanvasFrame(Frame):
    """
    Canvas Frame Class

    Description:
    Contains the loaded image and sets the mouse button click event
    """

    def __init__(self, parent, inputimage, *args, **kwargs):
        Frame.__init__(self, parent.frame)

        # Parent
        self.parent = parent

        # Load Image
        self.inputimage = inputimage
        filepath = 'lowpolypainter/resources/images/' + inputimage
        self.image = Image.open(filepath)
        self.background = ImageTk.PhotoImage(self.image)

        # Center Canvas
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Create Canvas
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.canvas.create_image(0, 0, image=self.background, anchor=NW)
        self.canvas.grid(row=1, column=1, sticky=NSEW)

        # Color Object
        self.color = Color(np.array(self.image), 0.5, 0.5)

        self.selectedFace = [False, None]

        # Mesh
        self.mesh = Mesh(self)

        # Selection
        self.selected = None

         # Mouse Event
        self.mouseEventHandled = False

        self.faceState = NORMAL

        # Events
        self.canvas.bind("<Button>", self.click)
        self.canvas.bind_all("<space>", func=self.toggleFaces)
        self.canvas.bind_all("<BackSpace>", self.deleteSelected)
        self.canvas.bind_all("<Key-Delete>", self.deleteSelected)

    """ EVENT """
    def click(self, event):
        """
        Canvas Click Event

        Description:
        Adds point to canvas, will draw line to last point while ctrl isn't pressed
        """
        eventPoint = [event.x, event.y]
        if self.inBounds(eventPoint) and not self.mouseEventHandled:
            self.parent.undoManager.do(self.parent)
            previousSelected = self.selected
            zoomedCoords = self.parent.zoom.FromViewport([event.x, event.y])
            self.mesh.addVertex([int(zoomedCoords[0]), int(zoomedCoords[1])])
            if (previousSelected is not None) and not (event.state & CTRL_MASK):
                self.mesh.addEdge(previousSelected, self.selected)
        self.mouseEventHandled = False

    def generateBorder(self, step):
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
        points = height_points_west
        points = np.vstack([points, height_points_east])

        # Width
        width_indices = np.arange(0, width, math.floor(width/step), dtype=int)
        width_indices[-1] = width - 1
        width_points_north = np.zeros((len(width_indices), 2), dtype=int)
        width_points_south = np.zeros((len(width_indices), 2), dtype=int)
        for i in range(len(width_points_north)):
            width_points_north[i][0] = width_indices[i]
            width_points_south[i] = [width_indices[i], height - 1]
        points = np.vstack([points, width_points_north])
        points = np.vstack([points, width_points_south])

        for point in points:
            self.mesh.addVertex([int(point[0]), int(point[1])])

    """ FACE """
    def toggleFaces(self, event):
        state = NORMAL
        if self.faceState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure("f", state=state)
        self.faceState = state

    """ GENERAL """
    def inBounds(self, point):
        x, y = point[0], point[1]
        return (x >= 0) and (y >= 0) and (x < self.width) and (y < self.height)

    def select(self, object):
        if (object != self.selected):
            self.deselect(self.selected)
            self.selected = object

    def deleteSelected(self, event):
        self.parent.undoManager.do(self.parent)
        if self.selected is not None:
            self.selected.delete()
            self.selected = None

    def deselect(self, object):
        if self.selected is not None:
            object.deselect()

    def clear(self):
        self.selectedFace = [False, None]
        self.mesh.clear()

    """ Triangulate """
    def triangulate(self, size=0, random=0, mask=None):
        if mask is None or len(mask[mask != 0]) == 0:
            mask = np.ones([self.width, self.height], dtype=bool)

        # Get points in mask
        points = []
        verts = np.asarray(self.mesh.bvertices)[mask]
        verts = verts[verts != 0.0]


        # Need min 4 points
        if len(verts) + size + random <= 3:
            return
        
        for vert in verts:
            vert.deconnect()
            points.append(vert.coords)
        points = np.asarray(points)

        triangulate = Triangulate(self.image, points)

        if size != 0:
            triangulate.generateCanny(mask=mask)

        triangle = triangulate.triangulate(size, random)

        # Generate Mesh Objects
        for tris in triangle:
            self.mesh.faceToVertexGeneration(triangulate.points[tris[0]],
                                             triangulate.points[tris[1]],
                                             triangulate.points[tris[2]])

        # Draw
        for face in self.mesh.faces:
            face.draw(False)

        for edge in self.mesh.edges:
            edge.draw(False)

        for vert in self.mesh.vertices:
            vert.draw(False)
            
            
    # inserts an image into canvas Frame by path
    def insert(self, path, name):
        self.inputimage = name
        if isinstance(path, basestring):
            self.image = Image.open(path)
        else:
            self.image = path
        self.background = ImageTk.PhotoImage(self.image)
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas.configure(width=self.width, height=self.height)
        self.canvas.create_image(0, 0, image=self.background, anchor=NW)
        
        self.color = Color(np.array(self.image), 0.5, 0.5)

        self.selectedFace = [False, None]

        # Mesh
        self.mesh = Mesh(self)

        # Selection
        self.selected = None

         # Mouse Event
        self.mouseEventHandled = False

        self.faceState = NORMAL
        
