# Python Modules
import time
import math
import numpy as np
from Tkinter import *
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
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Create Canvas
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.backgroundId = self.canvas.create_image(0, 0, image=self.background, anchor=NW)
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

        # Toggle Events
        self.faceState = NORMAL
        self.toggleState = NORMAL

        # Events
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind_all("<space>", func=self.toggleFaces)
        self.canvas.bind_all("<BackSpace>", self.deleteSelected)
        self.canvas.bind_all("<Key-Delete>", self.deleteSelected)
        self.canvas.bind_all("<Up>", func=self.toggleVertsAndEdges)

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
            if (previousSelected is not None) and (isinstance(previousSelected, Vertex)) and not (event.state & CTRL_MASK):
                self.mesh.addEdge(previousSelected, self.selected)
        self.mouseEventHandled = False

    """ FACE """
    def toggleFaces(self, event):
        state = NORMAL
        if self.faceState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure("f", state=state)
        self.faceState = state

    """ VERTICES AND EDGES """
    def toggleVertsAndEdges(self, event):
        state = NORMAL
        if self.toggleState is NORMAL:
            state = HIDDEN
        self.canvas.itemconfigure("v", state=state)
        self.canvas.itemconfigure("e", state=state)
        self.toggleState = state

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

    """ Border """
    def border(self, triangulate=False, step=6):
        # generate border points
        border = Border(self.width, self.height)

        if triangulate:
            if len(self.mesh.vertices) <= 4:
                return

            coords = []
            for vert in self.mesh.vertices:
                coords.append(vert.coords)

            # generate convex hull
            border.generateConvexHull(coords)

            # mark hull points
            for point in border.hull:
                id = self.mesh.bvertices[point[0]][point[1]].id
                self.canvas.itemconfigure(id, fill='yellow')

            # add corner points and edges
            corn_verts = []
            for i in range(len(border.corner)):
                hpoint = border.hull[border.corner[i]]
                hvert = self.mesh.bvertices[hpoint[0]][hpoint[1]]
                bvert = self.mesh.addVertex(border.points[i])
                self.mesh.addEdge(bvert, hvert)
                corn_verts.append(bvert)

            sort_verts_index = np.argsort(border.corner)

            sort_index = sort_verts_index[3]
            prev_vert = corn_verts[sort_index]
            for i in range(border.corner[scorner[3]]+1, len(border.hull)):
                hpoint = border.hull[i]
                # hvert = self.mesh.bvertices[hpoint[0]][hpoint[1]]
                # bvert = self.mesh.addVertex([border.hull[i][0], border.points[scorner[3]][1]])
                # self.mesh.addEdge(bvert, hvert)
                # self.mesh.addEdge(pbvert, hvert)
                # self.mesh.addEdge(pbvert, bvert)
                # pbvert = bvert

            for i in range(0, border.corner[0]):
                point = border.hull[i]
                id = self.mesh.bvertices[point[0]][point[1]].id
                self.canvas.itemconfigure(id, fill='red')

            prev_vert = vcorner[sort_vert[0]]
            for i in range(border.corner[scorner[0]]+1, border.corner[scorner[1]]):
                hpoint = border.hull[i]
                hvert = self.mesh.bvertices[hpoint[0]][hpoint[1]]
                bvert = self.mesh.addVertex([border.hull[i][0], border.points[scorner[0]][1]])
                self.mesh.addEdge(bvert, hvert)
                self.mesh.addEdge(pbvert, hvert)
                self.mesh.addEdge(pbvert, bvert)
                pbvert = bvert

            for i in range(border.corner[1]+1, border.corner[2]):
                point = border.hull[i]
                id = self.mesh.bvertices[point[0]][point[1]].id
                self.canvas.itemconfigure(id, fill='orange')

            for i in range(border.corner[2]+1, border.corner[3]):
                point = border.hull[i]
                id = self.mesh.bvertices[point[0]][point[1]].id
                self.canvas.itemconfigure(id, fill='magenta')












            return
            # draw border from border to hull
            bprev = None
            for bpoint in border.points:
                hvert = None
                minDistance = float('Inf')
                bvert = self.mesh.addVertex(bpoint)

                for hpoint in border.hull:
                    dist = math.sqrt((hpoint[0] - bpoint[0])**2 + (hpoint[1] - bpoint[1])**2)
                    if dist < minDistance:
                        minDistance = dist
                        hvert = self.mesh.bvertices[hpoint[0]][hpoint[1]]

                if hvert != None:
                    self.mesh.addEdge(bvert, hvert)
                    if bprev != None:
                        self.mesh.addEdge(bprev, bvert)
                        self.mesh.addEdge(bprev, hvert)
                    bprev = bvert


            return



            # triangulate hull and border
            if len(points) >= 4:

                triangulate = Triangulate(self.image, points)
                triangle = triangulate.triangulate(0, 0)

                # sort out connection between hull points
                for tris in triangle:
                    l = len(border.hull) - 1

                    if not (tris[0] < l and tris[1] < l and tris[2] < l):
                        point1 = points[tris[0]]
                        vert1 = self.mesh.bvertices[point1[0]][point1[1]]
                        self.canvas.itemconfigure(vert1.id, fill='yellow')
                        point2 = points[tris[1]]
                        vert2 = self.mesh.bvertices[point2[0]][point2[1]]
                        self.canvas.itemconfigure(vert2.id, fill='yellow')
                        point3 = points[tris[2]]
                        vert3 = self.mesh.bvertices[point3[0]][point3[1]]
                        self.canvas.itemconfigure(vert3.id, fill='yellow')
                        edge1 = self.mesh.addEdge(vert1, vert2)
                        if len(edge1.intersectingEdges) != 0:
                            edge1.delete()
                        edge2 = self.mesh.addEdge(vert2, vert3)
                        if len(edge2.intersectingEdges) != 0:
                            edge2.delete()
                        edge3 = self.mesh.addEdge(vert1, vert3)
                        if len(edge3.intersectingEdges) != 0:
                            edge3.delete()
        else:
            # draw border points
            for point in border.points:
                self.mesh.addVertex([int(point[0]), int(point[1])])




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
