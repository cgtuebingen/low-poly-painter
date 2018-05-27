# Python Modules
from Tkinter import *
from PIL import ImageTk, Image

# Local Modules
from lowpolypainter.mesh import Mesh

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
        self.canvasFrame.deleteFaces(self.mesh)
        self.mesh.clear()

    # Canvas is clicked at position
    def click(self, event):
        self.mesh.addVertex(event.x, event.y)
        # TODO: Remove redraw every face
        self.canvasFrame.drawFaces(self.mesh)

    # Create random mesh
    def random(self):
        self.mesh.addRandomVerticies(10)
        self.canvasFrame.drawFaces(self.mesh)


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
        self.canvasBackground = ImageTk.PhotoImage(Image.open(filepath))

        # Create Canvas
        self.frameWidth = self.canvasBackground.width()
        self.frameHeight = self.canvasBackground.height()
        self.canvas = Canvas(self, width = self.frameWidth, height = self.frameHeight)
        self.canvas.create_image(0, 0, image = self.canvasBackground, anchor = NW)

        # Canvas Button
        self.canvas.bind("<Button>", parent.click)
        self.canvas.grid()

    def drawFace(self, mesh, index):
        face = mesh.faces[index]
        vertex_1 = mesh.vertices[face.vertices[0]]
        vertex_2 = mesh.vertices[face.vertices[1]]
        vertex_3 = mesh.vertices[face.vertices[2]]
        self.canvas.create_polygon(vertex_1.x, vertex_1.y,
                                   vertex_2.x, vertex_2.y,
                                   vertex_3.x, vertex_3.y,
                                   fill = face.color, tag = 'face_' + str(index))

    def drawFaces(self, mesh):
        for index in range(0, len(mesh.faces)):
            self.drawFace(mesh, index)

    def deleteFace(self, index):
        self.canvas.delete('face_' + str(index))

    def deleteFaces(self, mesh):
        for index in range(0, len(mesh.faces)):
            self.deleteFace(index)


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
