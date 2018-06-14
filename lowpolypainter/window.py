# Python Modules
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image

# Local Modules
from lowpolypainter.mesh import Mesh
from lowpolypainter.color import Color
from lowpolypainter.export import export
from matrix3x3 import Matrix3x3
from vector3 import Vector3

# TODO: Design UI
# TODO: Split buttons and canvas into different frames
# TODO: Maybe create diffrent modules for canvas and buttons

"""
Window Class

Description:
Contains canvas and roots the application.
"""
class Window(object):

    def __init__(self, inputimage):
        self.root = Tk()

        # Settings
        self.root.config(bg = 'black')
        self.root.title('Low Poly Painter')

        # Frame
        self.frame = Frame(self.root, bg = 'white')
        self.frame.grid()

        # Canvas Frame
        self.canvasFrame = CanvasFrame(self, inputimage)
        self.canvasFrame.grid()

        # Button Frame
        self.buttonFrame = ButtonFrame(self)
        self.buttonFrame.grid()

        # Mesh
        self.mesh = Mesh(self.canvasFrame.frameWidth, self.canvasFrame.frameHeight)

    # Clear mesh and canvas
    def clear(self):
        self.canvasFrame.deleteObjects('point', 0,  len(self.mesh.vertices))
        self.canvasFrame.deleteObjects('line', 0,  len(self.mesh.edges))
        self.canvasFrame.deleteObjects('triangle', 0,  len(self.mesh.faces))
        self.mesh.clear()

    # Canvas is clicked at position
    def click(self, event):
        self.mesh.addVertex(event.x, event.y)

        # TODO: Remove this call
        self.addedVertexCreateFace()

    # Create random mesh
    # TODO: Remove this function
    def random(self):
        count = 10
        for x in range(count):
            x = np.random.randint(self.canvasFrame.frameWidth)
            y = np.random.randint(self.canvasFrame.frameHeight)
            self.mesh.addVertex(x, y)
            self.addedVertexCreateFace()

    # exports current mesh as svg image
    def export(self):
        export(self.mesh)


    # TODO: Remove this function
    # This function is just used for testing
    # This generates a face when the mesh has more then 3 verticies
    # A new face is instanced by the last three vertices in the vertices array
    # As soon as you add a new vertex to the mesh this function should be called
    def addedVertexCreateFace(self):
        zoomProjection = Matrix3x3.Identity()
        verticesLength = len(self.mesh.vertices)
        # FACE
        if (verticesLength >= 3):
            self.mesh.addFace(verticesLength - 3,
                              verticesLength - 2,
                              verticesLength - 1,
                              '#FFFFFF')

            face = self.mesh.faces[-1]
            verticesArray = [[self.mesh.vertices[face.vertices[0]].x,
                              self.mesh.vertices[face.vertices[0]].y],
                             [self.mesh.vertices[face.vertices[1]].x,
                              self.mesh.vertices[face.vertices[1]].y],
                             [self.mesh.vertices[face.vertices[2]].x,
                              self.mesh.vertices[face.vertices[2]].y]]

            face.color = Color.fromImage(self.canvasFrame.image, 0.05, verticesArray)
            self.canvasFrame.drawTriangle(self.mesh, len(self.mesh.faces) - 1, zoomProjection)
        # EDGE
        if (verticesLength >= 2):
            self.mesh.addEdge(verticesLength - 2,
                              verticesLength - 1)
            self.canvasFrame.drawLine(self.mesh, len(self.mesh.edges) - 1, zoomProjection)

        # VERTEX
        self.canvasFrame.drawPoint(self.mesh, len(self.mesh.vertices) - 1, zoomProjection)


"""
Canvas Frame Class

Description:
Contains the loaded image and a button.
The button detects the position clicked on the canvas.
"""
class CanvasFrame(Frame):

    def __init__(self, parent, inputimage, *args, **kwargs):
        Frame.__init__(self, parent.frame)

        # Load Image
        filepath = 'lowpolypainter/resources/images/' + inputimage
        self.image = Image.open(filepath)
        self.canvasBackground = ImageTk.PhotoImage(self.image)

        # Create Canvas
        self.frameWidth = self.canvasBackground.width()
        self.frameHeight = self.canvasBackground.height()
        self.canvas = Canvas(self, width = self.frameWidth, height = self.frameHeight)
        self.canvas.create_image(0, 0, image = self.canvasBackground, anchor = NW)

        # Canvas Button
        self.canvas.bind("<Button>", parent.click)
        self.canvas.grid()

    def drawPoint(self, mesh, index, projection):
        radius = 2
        color = '#0000FF'
        vertex = projection * mesh.vertices[index].Vector3()
        self.canvas.create_oval(vertex.x - radius,
                                vertex.y - radius,
                                vertex.x + radius,
                                vertex.y + radius,
                                 fill = color, tag = ('point', str(index)))

    def drawLine(self, mesh, index, projection):
        color = '#0000FF'
        edge = mesh.edges[index]
        vertex_1 = projection * mesh.vertices[edge.vertices[0]].Vector3()
        vertex_2 = projection * mesh.vertices[edge.vertices[1]].Vector3()
        self.canvas.create_line(vertex_1.x, vertex_1.y,
                                vertex_2.x, vertex_2.y,
                                 fill = color, tag = ('line', str(index)))
        self.canvas.tag_lower('line&&' + str(index), 'point&&0')

    def drawTriangle(self, mesh, index, projection):
        face = mesh.faces[index]
        vertex_1 = projection * mesh.vertices[face.vertices[0]].Vector3()
        vertex_2 = projection * mesh.vertices[face.vertices[1]].Vector3()
        vertex_3 = projection * mesh.vertices[face.vertices[2]].Vector3()
        self.canvas.create_polygon(vertex_1.x, vertex_1.y,
                                   vertex_2.x, vertex_2.y,
                                   vertex_3.x, vertex_3.y,
                                   fill = face.color, tag = ('triangle', str(index)))
        self.canvas.tag_lower('triangle&&' + str(index), 'line&&0')

    def deleteObject(self, object, index):
        self.canvas.delete(object + '&&' + str(index))

    def deleteObjects(self, object, startIndex, endIndex):
        for index in range(startIndex, endIndex):
            self.deleteObject(object, index)


"""
Button Frame Class

Description:
Contains two buttons for clearing and testing.
"""
class ButtonFrame(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)

        # Test Button
        self.testButton = Button(self, text='Random', command = parent.random)
        self.testButton.grid()

        # Clear Button
        self.clearButton = Button(self, text='Clear', command = parent.clear)
        self.clearButton.grid()

        # Export Button
        self.exportButton = Button(self, text="Export", command = parent.export)
        self.exportButton.grid()
