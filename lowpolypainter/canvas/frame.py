# Python Modules
import time
import math
import numpy as np
from Tkinter import *
from random import randint
from PIL import ImageTk, Image

# Local Modules
from mesh import Mesh
from lowpolypainter.color import Color
from lowpolypainter.triangulate.border import Border
from lowpolypainter.canvas.objects.vertex import Vertex
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
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(1, minsize='550')
        self.grid_rowconfigure(1, minsize='505')

        # Create Canvas
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas = Canvas(self, width='550', height='505', relief='flat', borderwidth='1', highlightbackground='#DADADA', highlightthickness='1')
        self.backgroundId = self.canvas.create_image(0, 0, image=self.background, anchor='nw')
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

        # Focus
        self.focus = True

        # Toggle Events
        self.vertsState = NORMAL
        self.edgesState = NORMAL
        self.faceState = NORMAL

        # Events
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind_all("<space>", func=self.toggleFacesCheckbutton)
        self.canvas.bind_all("<BackSpace>", self.deleteSelected)
        self.canvas.bind_all("<Key-Delete>", self.deleteSelected)
        self.canvas.bind_all("<Up>", func=self.toggleVertsCheckbutton)
        self.canvas.bind_all("<Down>", func=self.toggleEdgesCheckbutton)


    """ EVENT """
    def click(self, event):
        """
        Canvas Click Event

        Description:
        Adds point to canvas, will draw line to last point while ctrl isn't pressed
        """
        self.parent.root.focus()
        eventPoint = [event.x, event.y]
        if self.inBounds(eventPoint) and (not self.mouseEventHandled) and ((self.parent.controlMode=="Points") or (self.parent.controlMode=="Points and Lines")):
            self.parent.undoManager.do(self.parent)
            previousSelected = self.selected
            zoomedCoords = self.parent.zoom.FromViewport([event.x, event.y])
            self.mesh.addVertex([int(zoomedCoords[0]), int(zoomedCoords[1])])
            if (previousSelected is not None) and (isinstance(previousSelected, Vertex)) and (self.parent.controlMode == "Points and Lines") and not (event.state & CTRL_MASK):
                self.mesh.addEdge(previousSelected, self.selected)
        self.mouseEventHandled = False

    """ VERTICES """
    def toggleVerts(self, event=None):
        if not self.focus:
            return
        state = NORMAL
        if self.vertsState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure("v", state=state)
        self.vertsState = state

    """ EDGES """
    def toggleEdges(self, event=None):
        if not self.focus:
            return
        state = NORMAL
        if self.edgesState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure("e", state=state)
        self.edgesState = state

    """ FACE """
    def toggleFaces(self, event=None):
        if not self.focus:
            return
        state = NORMAL
        if self.faceState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure("f", state=state)
        self.faceState = state

    """ checks Button for Vertices and Edges """
    def toggleVertsCheckbutton(self, event=None):
        self.parent.zoomAndToggleFrame.toggleFrame.vertexCheckbox.toggle()
        self.toggleVerts(event)

    """ checks Button for Vertices and Edges """
    def toggleEdgesCheckbutton(self, event=None):
        self.parent.zoomAndToggleFrame.toggleFrame.edgesCheckbox.toggle()
        self.toggleEdges(event)

    """checks Button for Faces """
    def toggleFacesCheckbutton(self, event=None):
        self.parent.zoomAndToggleFrame.toggleFrame.facesCheckbox.toggle()
        self.toggleFaces(event)

    """ GENERAL """
    def inBounds(self, point):
        x, y = point[0], point[1]
        return (x >= 0) and (y >= 0) and (x < self.width) and (y < self.height)

    def select(self, object):
        if (object != self.selected):
            self.deselect(self.selected)
            self.selected = object

    def deleteSelected(self, event):
        if not self.focus:
            return

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

    """ Border """
    def border(self, triangulate=False, step=0):
        # generate border
        border = Border(self.width, self.height)

        if triangulate:
            if len(self.mesh.vertices) <= 4:
                return

            coords = []
            for vert in self.mesh.vertices:
                coords.append(vert.coords)

            # generate convex hull
            border.generateConvexHull(coords)

            # draw border and connect edges
            for site_idx in range(len(border.sites)):
                # draw first corner point
                rp = border.sites[site_idx][0]
                rv = self.mesh.bvertices[rp[0]][rp[1]]
                bp = border.sites_orientation[site_idx][0]
                bv = self.mesh.bvertices[bp[0]][bp[1]]
                if bv == 0:
                    bv = self.mesh.addVertex(bp)
                self.mesh.addEdge(rv, bv)
                past_rv = rv
                past_bv = bv

                # draw points inbetween
                for point_idx in range(1,len(border.sites[site_idx])-1):
                    rp = border.sites[site_idx][point_idx]
                    rv = self.mesh.bvertices[rp[0]][rp[1]]
                    bp = border.sites_orientation[site_idx][point_idx]
                    bv = self.mesh.addVertex(bp)
                    self.mesh.addEdge(rv, bv)
                    self.mesh.addEdge(rv, past_rv)
                    self.mesh.addEdge(rv, past_bv)
                    self.mesh.addEdge(bv, past_bv)
                    past_rv = rv
                    past_bv = bv

                # draw last corner point
                rp = border.sites[site_idx][-1]
                rv = self.mesh.bvertices[rp[0]][rp[1]]
                bp = border.sites_orientation[site_idx][-1]
                bv = self.mesh.bvertices[bp[0]][bp[1]]
                if bv == 0:
                    bv = self.mesh.addVertex(bp)
                self.mesh.addEdge(rv, bv)
                self.mesh.addEdge(rv, past_rv)
                self.mesh.addEdge(rv, past_bv)
                self.mesh.addEdge(bv, past_bv)

            # mark hull points
            # for point in border.hull:
            #     id = self.mesh.bvertices[point[0]][point[1]].id
            #     self.canvas.itemconfigure(id, fill='yellow')

        else:
            # draw border points
            border.generatePoints(step)
            for point in border.points:
                self.mesh.addVertex([int(point[0]), int(point[1])])

    """ Random """
    def random(self, size=0):
        if size == 0:
            return

        w, h = self.width - 1, self.height - 1
        random_points = np.zeros((size, 2), dtype=int)
        for i in range(size):
            point = [randint(0, w), randint(0, h)]
            if self.mesh.bvertices[point[0]][point[1]] == 0:
                self.mesh.addVertex(point)

    """ Triangulate """
    def triangulate(self, size=0, mask=None):
        if mask is None or len(mask[mask != 0]) == 0:
            mask = np.ones([self.width, self.height], dtype=bool)

        # Get points in mask
        points = []
        verts = np.asarray(self.mesh.bvertices)[mask]
        verts = verts[verts != 0.0]

        # Need min 4 points
        if len(verts) + size <= 3:
            return

        for vert in verts:
            vert.deconnect()
            points.append(vert.coords)
        points = np.asarray(points)

        triangulate = Triangulate(self.image, points)

        if size != 0:
            triangulate.generateCanny(mask=mask)

        triangle = triangulate.triangulate(size)

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
