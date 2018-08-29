# Python Modules
import time
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image
import tkMessageBox
import tkFileDialog
import os, errno

# Local Modules
from store import save, load, savePath, loadPath, saveState
from export import exportDialog
from canvas.frame import CanvasFrame
from triangulate.frame import MaskFrame
from triangulate.frame import TriangulateFrame
from zoomTransformer import ZoomTransformer
from Colorwheel import Colorwheel
from lowpolypainter.undoManager import UndoManager


class Window(object):
    """
    Window Class

    Description:
    Contains canvas and roots the application.
    """

    def __init__(self, inputimage):
        self.root = Tk()

        # Zoom
        self.zoom = ZoomTransformer()

        # Image Path
        self.inputimage = inputimage

        # Settings
        off_x = 0
        off_y = -100
        min_width = 800
        min_height = 400
        self.root.config(bg='white')
        self.root.resizable(True, False)
        self.root.title('Low Poly Painter')
        self.root.minsize(min_width, min_height)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        dist_right = int(self.root.winfo_screenwidth()/2 - min_width/2 + off_x)
        dist_down = int(self.root.winfo_screenheight()/2 - min_height/2 + off_y)
        self.root.geometry("+{}+{}".format(dist_right, dist_down))


        # Frame
        self.frame = Frame(self.root, bg='white')
        self.frame.grid(sticky=N+S+E+W)
        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)

        # Toolbar Frame
        self.toolbarFrame = ToolbarFrame(self)
        self.toolbarFrame.grid(row=0, column=0, columnspan=2, sticky=N+E+W)

        self.frame.bind_all("<MouseWheel>", self.mouse_wheel_wheel)
        self.frame.bind_all("<Button-4>", self.mouse_wheel_button)
        self.frame.bind_all("<Button-5>", self.mouse_wheel_button)

        self.frame.bind_all("<Control-z>", self.undo)
        self.frame.bind_all("<Control-y>", self.redo)
        self.frame.bind_all("<Control-s>", self.saveState)

        # Canvas Frame
        self.canvasFrameToogle = False
        self.canvasFrame = CanvasFrame(self, inputimage)
        self.canvasFrame.grid(row=1, column=0, sticky=NSEW)

        # Mask Frame
        self.maskFrame = MaskFrame(self, inputimage)

        # Detail Frame
        self.detailFrame = DetailFrame(self)
        self.detailFrame.grid(row=1, column=1, sticky=NSEW)


        # Color Safepoints
        self.colorWheelSafePoint1 = "black"
        self.colorWheelSafePoint2 = "black"
        self.colorWheelSafePoint3 = "black"

        self.undoManager = UndoManager()
        
        self.saveName = None
        # default save directory
        defaultDirectory = "lowpolypainter/resources/stored_mesh_data/"
        try:
            os.makedirs(defaultDirectory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    """ ZOOM """
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


    """ ACTIONS """
    def toogleCanvasFrame(self, event=None):
        if self.canvasFrameToogle:
            self.canvasFrameToogle = False
            self.maskFrame.grid_remove()
            self.canvasFrame.grid(row=1, column=0, sticky=NSEW)
            # print self.canvasFrame.canvas.winfo_width(), self.canvasFrame.canvas.winfo_height()
            # print self.maskFrame.canvas.winfo_width(), self.maskFrame.canvas.winfo_height()
        else:
            self.canvasFrameToogle = True
            self.canvasFrame.grid_remove()
            self.maskFrame.grid(row=1, column=0, sticky=NSEW)
            # print self.canvasFrame.canvas.winfo_width(), self.canvasFrame.canvas.winfo_height()
            # print self.maskFrame.canvas.winfo_width(), self.maskFrame.canvas.winfo_height()


    def insert(self, event=None):
        defaultDirectory = "lowpolypainter/resources/stored_mesh_data/"
        file_path = tkFileDialog.askopenfilename(initialdir = defaultDirectory, filetypes=[("all files","*"), ("python","*.py"), ("portable pixmap","*.ppm"), ("JPEG","*.jpg")])
        if file_path != "":
            if file_path.endswith('.py'):
                name = file_path[file_path.rindex('/')+1:]
                content = loadPath(file_path)
                image = Image.fromstring(content[0]['mode'], content[0]['size'], content[0]['pixels'])
                self.loadImage(image, name)
                self.canvasFrame.mesh.quickload(content[1])
                self.saveName = file_path
            else:
                self.loadImagePath(file_path)

    def clear(self, event=None):
        self.undoManager.do(self)
        # Colorwheel Speicherplaetze
        self.colorWheelSafePoint1 = "black"
        self.colorWheelSafePoint2 = "black"
        self.colorWheelSafePoint3 = "black"
        self.canvasFrame.clear()

    def export(self, event=None):
        exportDialog(self.canvasFrame.mesh, self.canvasFrame.width, self.canvasFrame.height)

    # currently unused
    def saveMeshData(self, event=None):
        save(self.canvasFrame.mesh.save(), self.inputimage)

    def loadMeshData(self, event=None):
        self.canvasFrame.mesh.load(load(self.inputimage))

    def saveMeshDataPath(self, path, event=None):
        savePath(self.canvasFrame.mesh.quicksave(), path)

    def loadMeshDataPath(self, path, event=None):
        self.canvasFrame.mesh.quickload(loadPath(path))
        
    def saveState(self, event=None):
        if self.saveName == None:
            self.saveStateAs()
        else:
            saveState(self.canvasFrame.mesh, self.canvasFrame.image, self.saveName)
    
    def saveStateAs(self, event=None):
        defaultDirectory = "lowpolypainter/resources/stored_mesh_data/"
        file_path = tkFileDialog.asksaveasfilename(initialdir = defaultDirectory, filetypes=[("python", "*.py")])
        if file_path != "":
            if not file_path.endswith('.py'):
                file_path += '.py'
            self.saveName = file_path
            self.saveState()
        

    # undoes the last change
    def undo(self, event=None):
        self.undoManager.undo(self)

    # redoes the last undo
    def redo(self, event=None):
        self.undoManager.redo(self)

    def generateBorder(self, borderpoints=6):
        self.canvasFrame.generateBorder(borderpoints)

    def generateBorderAndTriangulate(self, event=None):
        self.generateBorder()
        self.triangulate()

    def triangulate(self, size=0, random=0):
        self.undoManager.do(self)
        if self.canvasFrameToogle:
            self.toogleCanvasFrame()
            self.maskFrame.canvas.delete("v")
            self.canvasFrame.triangulate(size, random, self.maskFrame.mask)
            self.maskFrame.mask = np.zeros([self.maskFrame.width, self.maskFrame.height], dtype=bool)
        else:
            self.canvasFrame.triangulate(size, random)

    # check if a vertex is an outer vertex
    def updateOuterVertices(self):
        # reset vertex degrees to 0
        for vertex in self.canvasFrame.mesh.vertices:
            vertex.degree = 0

        # calculate degree of enclosing angles by surrounding faces
        for face in self.canvasFrame.mesh.faces:
            face.calcVerticesDegrees()

        # if enclosing angle degree is not 360 a vertex is an outer vertex
        for vertex in self.canvasFrame.mesh.vertices:
            vertex.updateIsOuter()

    # TODO: Move to detail view menu
    def colorwheel(self, event=None):
        if not self.canvasFrame.selectedFace[0]:
            tkMessageBox.showinfo("Error", "No face selected!")
            return
        cw = Tk()
        cw.title("Colorwheel")
        app = Colorwheel(self, cw)
        cw.mainloop()
        cw.destroy()
        self.canvasFrame.selectedFace[0]=False

    """ DETAIL VIEW """
    def show_triangulate(self, event=None):
        self.detailFrame.selectedFrame.grid_forget()
        self.detailFrame.triangulateFrame.grid(row=0, column=1, sticky=N+E+S+W)
        self.detailFrame.selectedFrame = self.detailFrame.triangulateFrame
        
    def loadImagePath(self, path):
        name = path[path.rindex('/')+1:]
        # changes in window
        self.clear()
        self.inputimage = name
        self.undoManager.clear()
        # changes in canvas
        self.canvasFrame.insert(path, name)
        # changes in maskFrame
        self.maskFrame.insert(path, name)
        # changes in frame
        self.frame.update()
        
    def loadImage(self, image, name):
        # changes in window
        self.clear()
        self.inputimage = name
        self.undoManager.clear()
        # changes in canvas
        self.canvasFrame.insert(image, name)
        # changes in maskFrame
        self.maskFrame.insert(image, name)
        # changes in frame
        self.frame.update()
        
        

class ToolbarFrame(Frame):
    """
    Toolbar Frame Class

    Description:
    Contains tools and visual states of canvas
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)
        self.parent = parent
        self.config(bg='#D8D8D8', width=47)
        self.grid_columnconfigure(0, weight=1)

        self.buttonFrame = ButtonFrame(self)
        self.buttonFrame.grid(row=0, sticky=N+E+S+W)

        self.bottomBorder = Frame(self, bg='#AAAAAA', height=1)
        self.bottomBorder.grid(row=1, sticky=N+E+S+W)

class ButtonFrame(Frame):
    """
    Button Frame Class

    Description:
    Contains two buttons for clearing and testing.
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.config(bg='#DADADA', height=46)
        self.grid_columnconfigure(7, weight=1)
        # self.grid_rowconfigure(0, weight=0)

        icon_0 = PhotoImage(file="./lowpolypainter/resources/icons/Insert.gif")
        icon_1 = PhotoImage(file="./lowpolypainter/resources/icons/Clear.gif")
        icon_2 = PhotoImage(file="./lowpolypainter/resources/icons/Canny.gif")
        icon_3 = PhotoImage(file="./lowpolypainter/resources/icons/Color.gif")
        icon_4 = PhotoImage(file="./lowpolypainter/resources/icons/Save.gif")
        icon_5 = PhotoImage(file="./lowpolypainter/resources/icons/Export.gif")
        icon_6 = PhotoImage(file="./lowpolypainter/resources/icons/Undo.gif")
        icon_7 = PhotoImage(file="./lowpolypainter/resources/icons/Redo.gif")
        icon_8 = PhotoImage(file="./lowpolypainter/resources/icons/Borders.gif")
        icon_9 = PhotoImage(file="./lowpolypainter/resources/icons/SaveAs.gif")

        options = {"height": 46, "width": 46, "bg":'#D8D8D8', "borderwidth":0}

        # Insert Button
        self.insertButton = Label(self, image=icon_0, **options)
        self.insertButton.image = icon_0
        self.insertButton.grid(row=0, column=0, sticky=N+E+S+W)
        self.insertButton.bind("<Button-1>", parent.parent.insert)

        # Clear Button
        self.clearButton = Label(self, image=icon_1, **options)
        self.clearButton.image = icon_1
        self.clearButton.grid(row=0, column=1, sticky=N+E+S+W)
        self.clearButton.bind("<Button-1>", parent.parent.clear)

        # Canny Button
        self.cannyButton = Label(self, image=icon_2, **options)
        self.cannyButton.image = icon_2
        self.cannyButton.grid(row=0, column=2, sticky=N+E+S+W)
        self.cannyButton.bind("<Button-1>", parent.parent.show_triangulate)

        # Colorwheel Button
        self.colorWheelButton = Label(self, image=icon_3, **options)
        self.colorWheelButton.image = icon_3
        self.colorWheelButton.grid(row=0, column=3, sticky=N+E+S+W)
        self.colorWheelButton.bind("<Button-1>", parent.parent.colorwheel)

        # Undo Button
        self.undoButton = Label(self, image=icon_6, **options)
        self.undoButton.image = icon_6
        self.undoButton.grid(row=0, column=4, sticky=N+E+S+W)
        self.undoButton.bind("<Button-1>", parent.parent.undo)

        # Redo Button
        self.redoButton = Label(self, image=icon_7, **options)
        self.redoButton.image = icon_7
        self.redoButton.grid(row=0, column=5, sticky=N+E+S+W)
        self.redoButton.bind("<Button-1>", parent.parent.redo)

        # Borders Button
        self.redoButton = Label(self, image=icon_8, **options)
        self.redoButton.image = icon_8
        self.redoButton.grid(row=0, column=6, sticky=N+E+S+W)
        self.redoButton.bind("<Button-1>", parent.parent.generateBorderAndTriangulate)

        # Space
        self.space = Label(self, height=2, bg='#DADADA', borderwidth=0)
        self.space.grid(row=0, column=7, sticky=N+E+S+W)

        # SaveAs Button
        self.SaveAsButton = Label(self, image=icon_9, **options)
        self.SaveAsButton.image = icon_9
        self.SaveAsButton.grid(row=0, column=8, sticky=N+E+S+W)
        self.SaveAsButton.bind("<Button-1>", parent.parent.saveStateAs)

        # Save Button
        self.saveButton = Label(self, image=icon_4, **options)
        self.saveButton.image = icon_4
        self.saveButton.grid(row=0, column=9, sticky=N+E+S+W)
        self.saveButton.bind("<Button-1>", parent.parent.saveState)

        # Export Button
        self.exportButton = Label(self, image=icon_5, **options)
        self.exportButton.image = icon_5
        self.exportButton.grid(row=0, column=10, sticky=N+E+S+W)
        self.exportButton.bind("<Button-1>", parent.parent.export)

class DetailFrame(Frame):
    """
    Detail Frame Class

    Description:
    Contains details about current selected tool
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)
        self.config(bg='#ECECEC', width=200)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)

        self.informationFrame = Frame(self, bg='#ECECEC', width=212)
        self.informationFrame.grid(row=0, column=1, sticky=N+E+S+W)
        self.selectedFrame = self.informationFrame

        self.triangulateFrame = TriangulateFrame(self)
        #self.triangulateFrame.grid(row=0, column=1, sticky=N+E+S+W)

        self.leftBorder = Frame(self, bg='#AAAAAA', width=1)
        self.leftBorder.grid(row=0, column=0, sticky=N+E+S+W)

# TODO: Move description to tags
"""
Place, select and move points and lines with the mouse.
A line to the next point will automatically be created, as long as CTRL is not pressed.
Faces are selected by simply clicking on them.
Please note that there is no visualisation if you select any face.
To connect two points with a line, or to split a line in two, hold the SHIFT button.
If a line creates one or more triangles, then they will be automatically added.
Delete selected objects with DEL.
Toggle the visibility of the faces with SPACE.
"""
