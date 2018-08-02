# Python Modules
import time
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image

# Local Modules
from store import save, load
from export import exportDialog
from canvas.frame import CanvasFrame
from zoomTransformer import ZoomTransformer
from Colorwheel import Colorwheel


class Window(object):
    """
    Window Class

    Description:
    Contains canvas and roots the application.
    """

    def __init__(self, inputimage):
        self.root = Tk()

        self.zoom = ZoomTransformer()

        self.inputimage = inputimage

        # Settings
        self.root.config(bg='black')
        self.root.title('Low Poly Painter')

        # Frame
        self.frame = Frame(self.root, bg='white')
        self.frame.grid()

        self.frame.bind_all("<MouseWheel>", self.mouse_wheel_wheel)
        self.frame.bind_all("<Button-4>", self.mouse_wheel_button)
        self.frame.bind_all("<Button-5>", self.mouse_wheel_button)

        # Canvas Frame
        self.canvasFrame = CanvasFrame(self, inputimage)
        self.canvasFrame.grid()

        # Button Frame
        self.buttonFrame = ButtonFrame(self)
        self.buttonFrame.grid()

        # HowTo text
        self.textFrame = TextFrame(self)
        self.textFrame.grid()

        # Colorwheel Speicherplaetze
        self.colorWheelSafePoint1 = "white"
        self.colorWheelSafePoint2 = "white"

    def clear(self):
        self.canvasFrame.clear()

    def export(self):
        exportDialog(self.canvasFrame.mesh, self.canvasFrame.width, self.canvasFrame.height)

    def saveMeshData(self):
        save(self.canvasFrame.mesh.save(), self.inputimage)

    def loadMeshData(self):
        self.canvasFrame.mesh.load(load(self.inputimage))

    def triangulate(self):
        self.canvasFrame.canny()

    def mouse_wheel_button(self, event):
        if event.num == 4:
            self.mouse_wheel(120, 0, 0)
        elif event.num == 5:
            self.mouse_wheel(-120, 0, 0)

    def mouse_wheel_wheel(self, event):
        self.mouse_wheel(event.delta, event.x, event.y)

    def mouse_wheel(self, delta, x, y):
        self.zoom.ZoomAt(2**(delta * 0.001), [x, y])
        self.canvasFrame.mesh.updatePositions()

    # TODO Recoloring and connect with face Selection
    def colorwheel(self):
        if not self.canvasFrame.selectedFace[0]:
            print "no face selected"
            return
        if self.canvasFrame.selectedFace[0]:
            print self.canvasFrame.selectedFace[1]
        cw = Tk()
        app = Colorwheel(master=cw)
        app.mainloop()
        cw.destroy()

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

        # Colorwheel Button
        self.colorWheelButton = Button(self, text='Colorwheel', command=parent.colorwheel)
        self.colorWheelButton.grid()

        # Save button
        self.saveButton = Button(self, text="Save", command=parent.saveMeshData)
        self.saveButton.grid()

class TextFrame(Frame):
    """
    Contains how to for the user interface
    """

    def __init__(self, parent):
        Frame.__init__(self, parent.frame)

        self.howToLabel = Label(self, text="""Place, select and move points and lines with the mouse.
A line to the next point will automatically be created, as long as CTRL is not pressed.
CTRL is also used to select faces.
Please note that there is no visualisation if you select any face and the colorwheel is not connected yet.
To connect two points with a line, or to split a line in two, hold the SHIFT button.
If a line creates one or more triangles, then they will be automatically added.
Delete selected objects with DEL.
Toggle the visibility of the faces with SPACE.""", anchor=NW, justify=LEFT)
        self.howToLabel.grid()
