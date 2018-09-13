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
        self.root.config(bg='#ECECEC')
        self.root.resizable(True, False)
        self.root.title('Low Poly Painter')
        self.root.minsize(min_width, min_height)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        dist_right = int(self.root.winfo_screenwidth()/2 - min_width/2 + off_x)
        dist_down = int(self.root.winfo_screenheight()/2 - min_height/2 + off_y)
        self.root.geometry("+{}+{}".format(dist_right, dist_down))


        # Frame
        self.frame = Frame(self.root, bg='#ECECEC')
        self.frame.grid(sticky=N+S+E+W)
        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)
        
        # Canvas Frame
        self.canvasFrameToggle = False
        self.canvasFrame = CanvasFrame(self, inputimage)
        self.canvasFrame.grid(row=1, column=1, sticky=NSEW)

        # Toolbar Frame
        self.toolbarFrame = ToolbarFrame(self)
        self.toolbarFrame.grid(row=1, column=0, sticky=N+E+W)

        self.frame.bind_all("<MouseWheel>", self.mouse_wheel_wheel)
        self.frame.bind_all("<Button-4>", self.mouse_wheel_button)
        self.frame.bind_all("<Button-5>", self.mouse_wheel_button)

        self.frame.bind_all("<Control-z>", self.undo)
        self.frame.bind_all("<Control-y>", self.redo)
        self.frame.bind_all("<Control-s>", self.saveState)
        
        #Title Frame
        self.titleFrame = Label(self.frame, text="Low Poly Painter", height=5)
        self.titleFrame.grid(row=0, column=1, sticky=NSEW)
        self.titleFrame.config(bg="#ECECEC")


        # Mask Frame
        self.maskFrame = MaskFrame(self, inputimage)

        # Detail Frame
        self.detailFrame = DetailFrame(self)
        self.detailFrame.grid(row=1, column=2, sticky=NSEW)
        
        # Zoom and Toggle Frame
        self.zoomAndToggleFrame = ZoomAndToggleFrame(self)
        self.zoomAndToggleFrame.grid(row=2, column=1, sticky=N+E+S+W)


        # Color Safepoints
        self.colorWheelSafePoint1 = "black"
        self.colorWheelSafePoint2 = "black"
        self.colorWheelSafePoint3 = "black"
        
        #Contol Modus
        self.controlMode = None
        self.changeModeToP()

        self.undoManager = UndoManager()
        
        self.saveName = None
        # default save directory
        defaultDirectory = "lowpolypainter/resources/stored_mesh_data/"
        try:
            os.makedirs(defaultDirectory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
                
    """ Control Mode"""
    def changeModeToP(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg="#AAAAAA")                                
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg="#D8D8D8")                                
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg="#D8D8D8")
        self.controlMode = "Points"
    
    def changeModeToPAL(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg="#D8D8D8")                                
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg="#AAAAAA")                                
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg="#D8D8D8")
        self.controlMode = "Points and Lines"
    
    def changeModeToSL(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg="#D8D8D8")                                
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg="#D8D8D8")                                
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg="#AAAAAA")
        self.controlMode = "Split Line"

    """ ZOOM """
    def mouse_wheel_button(self, event):
        if event.num == 4:
            self.mouse_wheel(120, 0, 0)
        elif event.num == 5:
            self.mouse_wheel(-120, 0, 0)

    def mouse_wheel_wheel(self, event):
        self.mouse_wheel(event.delta, event.x, event.y)

    def mouse_wheel(self, delta, x, y):
        delta = 2**(delta * 0.001)
        self.zoom.ZoomAt(delta, [x, y])
        #self.canvasFrame.mesh.updatePositions()
        self.canvasFrame.canvas.scale("all", x, y, delta, delta)
        
        currentScale = self.zoom.CurrentScale()
        backgroundPosition = self.zoom.ToViewport([0,0])

        width, height = self.canvasFrame.image.size
        new_size = int(currentScale * width), int(currentScale * height)
        self.canvasFrame.background = ImageTk.PhotoImage(self.canvasFrame.image.resize(new_size))
        self.canvasFrame.canvas.delete(self.canvasFrame.backgroundId)
        self.canvasFrame.backgroundId = self.canvasFrame.canvas.create_image(
            backgroundPosition[0], backgroundPosition[1],
            image=self.canvasFrame.background, anchor=NW)
        self.canvasFrame.canvas.lower(self.canvasFrame.backgroundId)


    """ ACTIONS """
    def toggleCanvasFrame(self, event=None):
        if self.canvasFrameToggle:
            self.canvasFrameToggle = False
            self.maskFrame.grid_remove()
            self.canvasFrame.grid(row=1, column=1, sticky=N+S+E+W)
        else:
            self.canvasFrameToggle = True
            self.canvasFrame.grid_remove()
            self.maskFrame.grid(row=1, column=1, sticky=N+S+E+W)

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
        if self.canvasFrameToggle:
            self.toggleCanvasFrame()
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
        
        image = Image.open("lowpolypainter/resources/images/open.png")
        icon_0 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/delete.png")
        icon_1 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/colorButton.png")
        icon_3 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/save.png")
        icon_4 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/export.png")
        icon_5 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/undo.png")
        icon_6 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/redo.png")
        icon_7 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/clear.png")
        icon_10 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/Points.png")
        icon_11 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/pointsAndLines.png")
        icon_12 = ImageTk.PhotoImage(image)
        image = Image.open("lowpolypainter/resources/images/splitLine.png")
        icon_13 = ImageTk.PhotoImage(image)

        options = {"height": 46, "width": 46, "bg":'#D8D8D8', "borderwidth":0}

        # Insert Button
        self.insertButton = Label(self, image=icon_0, **options)
        self.insertButton.image = icon_0
        self.insertButton.grid(row=0, column=0, sticky=N+E+S+W)
        self.insertButton.bind("<Button-1>", parent.parent.insert)
        
        # Save Button
        self.saveButton = Menubutton(self, image=icon_4, **options)
        self.saveButton.image = icon_4
        self.saveButton.grid(row=1, column=0, columnspan=2, sticky=N+E+S+W)
        self.saveButton.menu =  Menu (self.saveButton, tearoff = 0)
        self.saveButton.menu.add_checkbutton (label="Save", command=parent.parent.saveState)
        self.saveButton.menu.add_checkbutton (label="Save as...", command=parent.parent.saveStateAs)
        self.saveButton.config(menu=self.saveButton.menu)
        
        # Export Button
        self.exportButton = Label(self, image=icon_5, **options)
        self.exportButton.image = icon_5
        self.exportButton.grid(row=2, column=0, sticky=N+E+S+W)
        self.exportButton.bind("<Button-1>", parent.parent.export)

        # Space
        self.space = Frame(self, height=1, bg='#000000', borderwidth=0)
        self.space.grid(row=3, column=0, sticky=N+E+S+W)

        # Clear Button
        self.clearButton = Label(self, image=icon_1, **options)
        self.clearButton.image = icon_1
        self.clearButton.grid(row=4, column=0, sticky=N+E+S+W)
        self.clearButton.bind("<Button-1>", parent.parent.clear)

        # Delete Button
        self.deleteButton = Label(self, image=icon_10, **options)
        self.deleteButton.image = icon_10
        self.deleteButton.grid(row=5, column=0, sticky=N+E+S+W)
        self.deleteButton.bind("<Button-1>", parent.parent.canvasFrame.deleteSelected)

        # Undo Button
        self.undoButton = Label(self, image=icon_6, **options)
        self.undoButton.image = icon_6
        self.undoButton.grid(row=6, column=0, sticky=N+E+S+W)
        self.undoButton.bind("<Button-1>", parent.parent.undo)

        # Redo Button
        self.redoButton = Label(self, image=icon_7, **options)
        self.redoButton.image = icon_7
        self.redoButton.grid(row=7, column=0, sticky=N+E+S+W)
        self.redoButton.bind("<Button-1>", parent.parent.redo)
        
        
        # Space2
        self.space2 = Frame(self, height=1, bg='#000000', borderwidth=0)
        self.space2.grid(row=8, column=0, sticky=N+E+S+W)
        
        
        # Colorwheel Button
        self.colorWheelButton = Label(self, image=icon_3, **options)
        self.colorWheelButton.image = icon_3
        self.colorWheelButton.grid(row=9, column=0, sticky=N+E+S+W)
        self.colorWheelButton.bind("<Button-1>", parent.parent.colorwheel)

        
        # Change to Points Mode
        self.pointsButton = Label(self, image=icon_11, **options)
        self.pointsButton.image = icon_11
        self.pointsButton.grid(row=10, column=0, sticky=N+E+S+W)
        self.pointsButton.bind("<Button-1>", parent.parent.changeModeToP)
        
        # Change to Points and Lines Mode
        self.pointsAndLinesButton = Label(self, image=icon_12, **options)
        self.pointsAndLinesButton.image = icon_12
        self.pointsAndLinesButton.grid(row=11, column=0, sticky=N+E+S+W)
        self.pointsAndLinesButton.bind("<Button-1>", parent.parent.changeModeToPAL)
        
        # Change to Split Line Mode
        self.splitLineButton = Label(self, image=icon_13, **options)
        self.splitLineButton.image = icon_13
        self.splitLineButton.grid(row=12, column=0, sticky=N+E+S+W)
        self.splitLineButton.bind("<Button-1>", parent.parent.changeModeToSL)
        
        
        

class DetailFrame(Frame):
    """
    Detail Frame Class

    Description:
    Contains details about current selected tool
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)
        self.parent = parent
        self.config(bg='#ECECEC', width=5)

        self.grid_rowconfigure(1, weight=1, uniform="detailframe")
        self.grid_rowconfigure(3, weight=1, uniform="detailframe")

        self.informationFrame = Frame(self, bg='#ECECEC', width=1)
        self.informationFrame.grid(row=1, column=1, sticky=N+E+S+W)
        
        #TODO: insert color wheel
        self.colorWheel = Label(self, width=5, height=10, text="insert Color Wheel here")
        self.colorWheel.config(bg='#ECECEC') 

        self.triangulateFrame = TriangulateFrame(self)
        #self.triangulateFrame.grid(row=0, column=1, sticky=N+E+S+W)
        
        self.colorWheel.grid(row=1, column=1, sticky=N+E+S+W)
        self.triangulateFrame.grid(row=3, column=1, sticky=N+E+S+W)

        self.leftBorder = Frame(self, bg='#AAAAAA', width=1)
        self.leftBorder.grid(row=0, column=0, rowspan=5, sticky=N+E+S+W)
        
        self.upperBorder = Frame(self, bg="#AAAAAA", height=1)
        self.upperBorder.grid(row=0, column=0, columnspan=3, sticky=N+E+S+W)
        
        self.middleLine = Frame(self, bg="#AAAAAA", height=1)
        self.middleLine.grid(row=2, column=0, columnspan=3, sticky=N+E+S+W)
        
        self.lowerBorder = Frame(self, bg="#AAAAAA", height=1)
        self.lowerBorder.grid(row=4, column=0, columnspan=3, sticky=N+E+S+W)
        

class ZoomAndToggleFrame(Frame):
    """
    Zoom And Toggle Frame Class
    
    Description:
    Contains Zoom Frame and Toggle Frame
    """
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)
        self.config(bg='#ECECEC', height=1)
        self.parent=parent
        self.zoomFrame=ZoomFrame(self)
        self.toggleFrame=ToggleFrame(self)
        self.spaceFrame=Label(self, bg='#ECECEC', width=5)
        self.grid_columnconfigure(0, weight=2, uniform="ZoomAndToggle")
        self.grid_columnconfigure(1, weight=1, uniform="ZoomAndToggle")
        self.grid_columnconfigure(2, weight=2, uniform="ZoomAndToggle")
        self.toggleFrame.grid(row=0, column=0, sticky=N+E+S+W)
        self.spaceFrame.grid(row=0, column=1, sticky=N+E+S+W)
        self.zoomFrame.grid(row=0, column=2, sticky=E)


class ZoomFrame(Frame):
    """
    Zoom Frame Class
    
    Description:
    Contains two Zoom Buttons
    """
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.config(bg='#ECECEC')
        self.grid_columnconfigure(0, weight=2, uniform="zoomFrame")
        self.grid_columnconfigure(1, weight=1, uniform="zoomFrame")
        self.grid_columnconfigure(2, weight=1, uniform="zoomFrame")
        self.grid_columnconfigure(3, weight=1, uniform="zoomFrame")
        
        # Label
        self.text = Label(self, text="Zoom:", height=1, width=5)
        self.text.grid(row=0, column=0, sticky=E)
        self.text.config(bg='#ECECEC')
                    
        # zoom-in Button
        self.zoomInButton = Button(self, text="+", command=lambda: parent.parent.mouse_wheel(120, 0, 0))
        self.zoomInButton.grid(row=0, column=1, sticky=W) 
        
        # zoom-out Button
        self.zoomOutButton = Button(self, text="-", command=lambda: parent.parent.mouse_wheel(-120, 0, 0))
        self.zoomOutButton.grid(row=0, column=2, sticky=W)
        
        # space
        self.spaceFrame = Frame(self, bg="#ECECEC")
        self.spaceFrame.grid(row=0, column=3, sticky=W)

class ToggleFrame(Frame):
    """
    Toogle Frame Class
    
    Descripton:
    Contains the Toggle Checkboxes
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.config(bg="#ECECEC")
                    
        # Label
        self.frame = Label(self, height=1, text="Show...")
        self.frame.grid(row=0, column=0, sticky=NSEW)
        self.frame.config(bg="#ECECEC")
                          
        # space
        self.placeholder1 = Label(self, width=1, bg="#ECECEC")
        self.placeholder1.grid(row=0, column=1, sticky=NSEW)
        
        # Checkbox for Vertices and Edges
        self.vertexCheckbox = Checkbutton(self, text="Vertices and Edges", command=parent.parent.canvasFrame.toggleVertsAndEdges)
        self.vertexCheckbox.grid(row=0, column=2, sticky=NSEW)
        self.vertexCheckbox.select()
        
        # Checkbox for Faces
        self.facesCheckbox = Checkbutton(self, text="Faces", command=parent.parent.canvasFrame.toggleFaces)
        self.facesCheckbox.grid(row=0, column=3, sticky=NSEW)
        self.facesCheckbox.select()
        
        
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
