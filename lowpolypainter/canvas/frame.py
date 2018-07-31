# Python Modules
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image

# Local Modules
from mesh import Mesh
from lowpolypainter.canny import Canny
from lowpolypainter.color import Color

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

        # Create Canvas
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.canvas.create_image(1, 1, image=self.background, anchor=NW)
        self.canvas.grid()

        # Color Object
        self.color = Color(np.array(self.image), 0.5, 0.5)

        self.selectedFace = [False, None]

        # Mesh
        self.mesh = Mesh(self)

        # Selection
        self.selected = None

         # Mouse Event
        self.mouseEvent = False

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
        if self.inBounds(eventPoint) and not self.mouseEvent:
            if (event.state & CTRL_MASK):
                iaf = self.mesh.insideAFace(eventPoint)
                if iaf[0]:
                    self.selectedFace = iaf
                    return
            self.selectedFace=[False, None]
            previousSelected = self.selected
            self.mesh.addVertex([event.x, event.y])
            if (previousSelected is not None) and not (event.state & CTRL_MASK):
                self.mesh.addEdge(previousSelected, self.selected)
        self.mouseEventHandled = False

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
        if self.selected is not None:
            self.selected.delete()
            self.selected = None

    def deselect(self, object):
        if self.selected is not None:
            object.deselect()

    def clear(self):
        self.mesh.clear()

    """ CANNY """
    def canny(self):
        canny = Canny(self.inputimage)
        canny.generateCorners()
        canny.generateCanny(99, 100)
        triangle = canny.generateDelaunay()

        self.mesh.addVertex(canny.points[0])
        self.mesh.addVertex(canny.points[1])
        self.mesh.addVertex(canny.points[2])
        self.mesh.addVertex(canny.points[3])
        self.mesh.addVertex(canny.points[4])
        self.mesh.addVertex(canny.points[5])
