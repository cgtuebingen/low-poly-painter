# Python Modules
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image
import time
from random import randint

# Local Modules
from lowpolypainter.mesh import Mesh
from lowpolypainter.color import Color
from lowpolypainter.export import exportDialog
from lowpolypainter.triangulation import bowyerWatson
from lowpolypainter.CanvasObjects import *
from zoomTransformer import ZoomTransformer
from CanvasObjectsMesh import CanvasObjectsMesh


# TODO: Design UI
# TODO: Split buttons and canvas into different frames
# TODO: Maybe create diffrent modules for canvas and buttons


class Window(object):
    """
    Window Class

    Description:
    Contains canvas and roots the application.
    """

    def __init__(self, inputimage):
        self.root = Tk()

        self.zoom = ZoomTransformer()

        # Settings
        self.root.config(bg='black')
        self.root.title('Low Poly Painter')

        # Frame
        self.frame = Frame(self.root, bg='white')
        self.frame.grid()

        # Canvas Frame
        self.canvasFrame = CanvasFrame(self, inputimage)
        self.canvasFrame.grid()

        # Button Frame
        self.buttonFrame = ButtonFrame(self)
        self.buttonFrame.grid()

        # HowTo text
        self.textFrame = TextFrame(self)
        self.textFrame.grid()

    # Clear mesh and canvas
    def clear(self):
        self.canvasFrame.clear()

    # exports current mesh as svg image
    def export(self):
        exportDialog(self.canvasFrame.canvasObjectsMesh, self.canvasFrame.frameWidth, self.canvasFrame.frameHeight)

    def triangulate(self):
        mesh = self.canvasFrame.toMesh()
        # TODO: Add triangulate call here
        # mesh = bowyerWatson(mesh)
        self.canvasFrame.fromMesh(mesh)

    def addMultipleElements(self):
        NUM_POINTS = 5000
        NUM_FACES = 5000

        width = self.canvasFrame.frameWidth
        height = self.canvasFrame.frameHeight
        mesh = Mesh(width, height)

        t = time.time()
        for i in range(NUM_POINTS):
            mesh.addVertex(randint(1, width), randint(1, height))

        for i in range(NUM_FACES):
            i1 = randint(0, NUM_POINTS - 1)
            i2 = i1
            i3 = i1

            while i1 == i2:
                i2 = randint(0, NUM_POINTS - 1)

            while i1 == i3 or i2 == i3:
                i3 = randint(0, NUM_POINTS - 1)

            mesh.addFace(i1, i2, i3, "#fff")

        print("Time to add faces to mesh:", time.time() - t)
        t = time.time()
        self.canvasFrame.fromMesh(mesh)
        print("Time to add faces to canvas:", time.time() - t)

        print("Num faces: ", len(self.canvasFrame.canvasObjectsMesh.faces))

    def addMultipleElementsCanvasMesh(self):
        NUM_POINTS = 5000
        NUM_FACES = 5000

        width = self.canvasFrame.frameWidth
        height = self.canvasFrame.frameHeight

        canvasMesh = self.canvasFrame.canvasObjectsMesh

        self.canvasFrame.clear()

        t = time.time()
        for i in range(NUM_POINTS):
            canvasMesh.addPoint(randint(1, width), randint(1, height))

        for i in range(NUM_FACES):
            i1 = randint(0, NUM_POINTS - 1)
            i2 = i1
            i3 = i1

            while i1 == i2:
                i2 = randint(0, NUM_POINTS - 1)

            while i1 == i3 or i2 == i3:
                i3 = randint(0, NUM_POINTS - 1)

            p1 = canvasMesh.points[i1]
            p2 = canvasMesh.points[i2]
            p3 = canvasMesh.points[i3]
            canvasMesh.addFaceFromPoints(p1, p2, p3)

        print("Time to add faces to CanvasMesh:", time.time() - t)
        print("Num faces: ", len(canvasMesh.faces))


class CanvasFrame(Frame):
    """
    Canvas Frame Class

    Description:
    Contains the loaded image and sets the mouse button click event
    """

    def __init__(self, parent, inputimage, *args, **kwargs):
        Frame.__init__(self, parent.frame)

        self.parent = parent

        # Load Image
        filepath = 'lowpolypainter/resources/images/' + inputimage
        self.image = Image.open(filepath)
        self.canvasBackground = ImageTk.PhotoImage(self.image)

        # Create Canvas
        self.frameWidth = self.canvasBackground.width()
        self.frameHeight = self.canvasBackground.height()
        self.canvas = Canvas(self, width=self.frameWidth, height=self.frameHeight)
        self.canvas.create_image(1, 1, image=self.canvasBackground, anchor=NW)
        self.canvas.grid()

        # Color Object
        self.color = Color(np.array(self.image), 0.5, 0.5)

        # Mesh
        self.canvasObjectsMesh = CanvasObjectsMesh(self)

        # Selection
        self.selectedPoint = None
        self.selectedLine = None

        self.mouseEventHandled = False

        self.currentFaceState = NORMAL

        # Events
        self.canvas.bind("<Button>", self.click)
        self.canvas.bind_all("<Key-Delete>", self.deleteSelected)
        self.canvas.bind_all("<space>", func=self.toggleFaces)

    def click(self, event):
        # vertex = self.zoom.FromViewport([event.x, event.y])
        # self.mesh.addVertex(vertex[0], vertex[1])
        """
        Handles the clicking on the canvas to add new points.
        Will automatically add a line from the last selected point if CTRL is not pressed.
        :param event:
        :return: None
        """

        # Ignore events out of bounds
        if (event.x < 0) or (event.y < 0) or (event.x >= self.frameWidth) or (
                event.y >= self.frameHeight):
            return

        # If an element of the canvas is clicked that has its own event handler, then it will set this property
        if not self.mouseEventHandled:
            vertex = self.parent.zoom.FromViewport([event.x, event.y])
            prevSelectedPoint = self.selectedPoint
            self.addPoint(int(vertex[0]), int(vertex[1]))

            # Pressing CTRL prevents the automatic line
            ctrlMask = 0x0004
            if (prevSelectedPoint is not None) and not (event.state & ctrlMask):
                self.addLine(prevSelectedPoint, self.selectedPoint)

        self.mouseEventHandled = False

    def addFace(self, line1, line2, line3):
        return self.canvasObjectsMesh.addFace(line1, line2, line3)

    def addFaceFromPoints(self, point1, point2, point3):
        return self.canvasObjectsMesh.addFace(point1, point2, point3)

    def addLine(self, point1, point2):
        return self.canvasObjectsMesh.addLine(point1, point2)

    def addPoint(self, x, y):
        return self.canvasObjectsMesh.addPoint(x, y)

    def toggleFaces(self, event):
        state = NORMAL
        if self.currentFaceState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure(TAG_FACE, state=state)
        self.currentFaceState = state

    def deleteSelected(self, event):
        if self.selectedPoint is not None:
            self.selectedPoint.delete()
            self.selectedPoint = None

        if self.selectedLine is not None:
            self.selectedLine.delete()
            self.selectedLine = None

    def deactivateSelected(self):
        if self.selectedPoint is not None:
            self.selectedPoint.deactivate()
        self.selectedPoint = None

        if self.selectedLine is not None:
            self.selectedLine.deactivate()
        self.selectedLine = None

    def selectPoint(self, point):
        self.deactivateSelected()
        point.select()
        self.selectedPoint = point

    def selectLine(self, line):
        self.deactivateSelected()
        line.select()
        self.selectedLine = line

    def getColorFromImage(self, coords):
        return self.color.fromImage(coords)

    def toMesh(self):
        return self.canvasObjectsMesh.toMesh()

    def fromMesh(self, mesh):
        self.canvasObjectsMesh.fromMesh(mesh)

    def clear(self):
        self.canvasObjectsMesh.clear()

class ButtonFrame(Frame):
    """
    Button Frame Class

    Description:
    Contains two buttons for clearing and testing.
    """

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)

        # Clear Button
        self.clearButton = Button(self, text='Clear', command=parent.clear)
        self.clearButton.grid()

        # Export Button
        self.exportButton = Button(self, text="Export", command=parent.export)
        self.exportButton.grid()

        # Triangulation Button
        self.triangulationButton = Button(self, text="Triangulize", command=parent.triangulate)
        self.triangulationButton.grid()

        # Test add multiple Button
        self.addButton = Button(self, text="Add multiple elements Mesh", command=parent.addMultipleElements)
        self.addButton.grid()

        # Test add multiple Button
        self.add2Button = Button(self, text="Add multiple elements CanvasMesh", command=parent.addMultipleElementsCanvasMesh)
        self.add2Button.grid()

class TextFrame(Frame):
    """
    Contains how to for the user interface
    """

    def __init__(self, parent):
        Frame.__init__(self, parent.frame)

        self.howToLabel = Label(self, text="""Place, select and move points and lines with the mouse.
A line to the next point will automatically be created, as long as CTRL is not pressed.
To connect two points with a line, or to split a line in two, hold the SHIFT button.
If a line creates one or more triangles, then they will be automatically added.
Delete selected objects with DEL.
Toggle the visibility of the faces with SPACE.""", anchor=NW, justify=LEFT)
        self.howToLabel.grid()
