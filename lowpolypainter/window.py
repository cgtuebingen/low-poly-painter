# Python Modules
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image

# Local Modules
from lowpolypainter.mesh import Mesh
from lowpolypainter.export import export
from lowpolypainter.triangulation import bowyerWatson
from lowpolypainter.CanvasObjects import *
from zoomTransformer import ZoomTransformer


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
        export(self.canvasFrame.toMesh())

    def triangulate(self):
        mesh = self.canvasFrame.toMesh()
        # TODO: Add triangulate call here
        # mesh = bowyerWatson(mesh)
        self.canvasFrame.fromMesh(mesh)


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

        # Canvas Button
        self.canvas.bind("<Button>", self.click)
        self.canvas.bind_all("<Key-Delete>", self.deleteSelected)
        self.canvas.grid()

        # Lists for the points/lines/faces
        self.points = []
        self.selectedPoint = None
        self.lines = []
        self.selectedLine = None
        self.faces = []

        self.selectedPoint = None

        self.mouseEventHandled = False

        self.currentFaceState = NORMAL
        self.canvas.bind_all("<space>", func=self.toggleFaces)

    def click(self, event):
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
            prevSelectedPoint = self.selectedPoint
            self.addPoint(event.x, event.y)

            # Pressing CTRL prevents the automatic line
            ctrlMask = 0x0004
            if (prevSelectedPoint is not None) and not (event.state & ctrlMask):
                self.addLine(prevSelectedPoint, self.selectedPoint)

        self.mouseEventHandled = False
        self.clickedPoint = None

    def toggleFaces(self, event):
        state = NORMAL
        if self.currentFaceState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure(TAG_FACE, state=state)
        self.currentFaceState = state

    def deleteSelected(self, event):
        print("Delete")
        if self.selectedPoint is not None:
            self.selectedPoint.delete()
            self.selectedPoint = None

        if self.selectedLine is not None:
            self.selectedLine.delete()
            self.selectedLine = None

    def addFace(self, line1, line2, line3):
        face = CanvasFace(line1, line2, line3, self)
        self.faces.append(face)
        return face

    def addLine(self, point1, point2):
        # Check if line to selected point already exists
        for line in point1.connectedLines:
            if line.isConnectedTo(point2):
                return line
        line = CanvasLine(point1, point2, self)
        self.lines.append(line)
        return line

    def addPoint(self, x, y):
        point = CanvasPoint(x, y, self)
        self.points.append(point)
        return point

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

    def toMesh(self):
        mesh = Mesh(self.frameWidth, self.frameHeight)
        pointIndices = []

        # Add all vertices
        for point in self.points:
            i = mesh.addVertex(point.x, point.y)
            pointIndices.append(i)

        # Add all lines
        for line in self.lines:
            point1 = line.points[0]
            point2 = line.points[1]

            i1 = pointIndices[self.points.index(point1)]
            i2 = pointIndices[self.points.index(point2)]

            mesh.addEdge(i1, i2)

        # Add all faces
        for face in self.faces:
            points = face.getPoints()
            i1 = pointIndices[self.points.index(points[0])]
            i2 = pointIndices[self.points.index(points[1])]
            i3 = pointIndices[self.points.index(points[2])]

            face.getAutoColor()

            mesh.addFace(i1, i2, i3, face.color)

        print(len(mesh.vertices), len(mesh.edges), len(mesh.faces))

        return mesh

    def fromMesh(self, mesh):
        self.clear()

        # Points
        for point in mesh.vertices:
            self.points.append(CanvasPoint(point.x, point.y, self.canvas, self))

        # Lines
        for line in mesh.edges:
            self.lines.append(
                (CanvasLine(self.points[line.vertices[0]], self.points[line.vertices[1]], self.canvas, self)))

        # if the edges of the face where not in the edges list, then add them now
        for face in mesh.faces:
            points = []
            for i in range(3):
                points.append(self.points[face.vertices[i]])

            # Check that all lines of the face are there and if not, then create them
            for i, j in [(0, 1), (1, 2), (2, 0)]:
                if not points[i].hasConnectingLine(points[j]):
                    self.addLine(points[i], points[j])

    def clear(self):
        self.points = []
        self.lines = []
        self.faces = []
        self.canvas.delete(TAG_POINT)
        self.canvas.delete(TAG_LINE)
        self.canvas.delete(TAG_FACE)
        self.selectedPoint = None


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
