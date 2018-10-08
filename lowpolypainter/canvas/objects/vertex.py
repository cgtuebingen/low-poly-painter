import math
import numpy as np

from lowpolypainter.controlMode import Mode, NUM_RIGHT_CLICK

# TAG
TAG_VERTEX = "v"
TAG_EDGE = "e"
TAG_FACE = "f"

# SIZE
RADIUS = 2
LARGE_RADIUS = 5

# COLOR
COLOR_BORDER = "#FFFFFF"
COLOR_DEFAULT = "#3B99FC"
COLOR_SELECTED = "#ff0000"

# MASK
MASK_SHIFT = 0x0001


class Vertex:
    """
    Vertex

    Functions:
    Handels Vetex creation, movement, selection and updating
    """

    def __init__(self, coords, frame, user=True):
        # Information
        self.id = -1
        self.coords = coords

        # Part of edges
        self.edges = []

        # Dependencies
        self.parent = frame

        # trace start of movement
        self.firstMove = True

        # User clicked canvas
        if not user:
            return

        # Update
        self.draw()

        # Select
        self.select()
        self.parent.select(self)

    """ EVENTS """
    def clickHandle(self, event):
        '''
        Right click on vertex: Creates edge to vertex
        Default click on vertex: Sets vertex as selected
        '''
        self.parent.mouseEventHandled = True
        if ((self.parent.parent.controlMode.mode == Mode.CONNECT_OR_SPLIT) or
            (event.num == NUM_RIGHT_CLICK)) and \
                (self.parent.selected is not None) and \
                (isinstance(self.parent.selected, Vertex)):
            self.parent.parent.undoManager.do(self.parent.parent)
            self.parent.mesh.addEdge(self, self.parent.selected)
        self.select()
        self.parent.select(self)

    def moveHandle(self, event):
        if self.firstMove:
            self.parent.mesh.bvertices[int(self.coords[0])][int(self.coords[1])] = 0
            self.parent.parent.undoManager.do(self.parent.parent)
            self.firstMove = False
        zoomedCoords = self.parent.parent.zoom.FromViewport([event.x, event.y])
        self.move(self.moveInBounds([int(zoomedCoords[0]), int(zoomedCoords[1])]))
        self.expand(event)


    def releaseHandle(self, event):
        if self.firstMove == True:
            return
        # Merge verts when dropped on same position
        self.firstMove = True
        x, y = int(self.coords[0]), int(self.coords[1])
        x_0, x_1 = x - 3 if x - 3 > 0 else 0 , x + 3
        y_0, y_1 = y - 3 if y - 3 > 0 else 0 , y + 3
        verts_arr = np.asarray(self.parent.mesh.bvertices)[x_0:x_1,y_0:y_1]
        verts = verts_arr[verts_arr != 0.0]

        min_dist_vert = None
        min_dist = float('Inf')

        for vert in verts:
            point = vert.coords
            dist = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
            if dist < min_dist:
                min_dist = dist
                min_dist_vert = vert
        if min_dist_vert != None:
            self.mergeWithVertex(min_dist_vert)
        self.parent.mesh.bvertices[x][y] = self
        self.parent.mouseEvent = False

    def expand(self, event=None):
        visualCoords = self.getVisualCoords()
        self.parent.canvas.coords(self.id, visualCoords[0] - LARGE_RADIUS,
                                          visualCoords[1] - LARGE_RADIUS,
                                          visualCoords[0] + LARGE_RADIUS,
                                          visualCoords[1] + LARGE_RADIUS)

    def shrink(self, event=None):
        visualCoords = self.getVisualCoords()
        self.parent.canvas.coords(self.id, visualCoords[0] - RADIUS,
                                          visualCoords[1] - RADIUS,
                                          visualCoords[0] + RADIUS,
                                          visualCoords[1] + RADIUS)

    """ GENERAL """
    def draw(self, user=False):
        visualCoords = self.getVisualCoords()
        self.id = self.parent.canvas.create_oval(visualCoords[0] - RADIUS,
                                          visualCoords[1] - RADIUS,
                                          visualCoords[0] + RADIUS,
                                          visualCoords[1] + RADIUS,
                                          outline = COLOR_BORDER,
                                          fill = COLOR_DEFAULT,
                                          tag = TAG_VERTEX,
                                          state= self.parent.vertsState)

        self.parent.canvas.tag_bind(self.id, sequence="<Button>", func=self.clickHandle)
        self.parent.canvas.tag_bind(self.id, sequence="<B1-Motion>", func=self.moveHandle)
        self.parent.canvas.tag_bind(self.id, sequence="<ButtonRelease-1>", func=self.releaseHandle)
        self.parent.canvas.tag_bind(self.id, sequence="<Enter>", func=self.expand)
        self.parent.canvas.tag_bind(self.id, sequence="<Leave>", func=self.shrink)

        if user:
            self.parent.canvas.tag_raise(self.id, TAG_VERTEX)

    def updatePosition(self):
        visualCoords = self.getVisualCoords()
        self.parent.canvas.coords(self.id, visualCoords[0] - RADIUS,
                                          visualCoords[1] - RADIUS,
                                          visualCoords[0] + RADIUS,
                                          visualCoords[1] + RADIUS)

    def select(self):
        self.parent.canvas.itemconfigure(self.id, fill=COLOR_SELECTED)
        self.parent.canvas.tag_raise(self.id, TAG_VERTEX)

    def deselect(self):
        self.parent.canvas.itemconfigure(self.id, fill=COLOR_DEFAULT)


    def move(self, vert, low=False):
        self.coords = vert
        self.updatePosition()
        self.moveEdges(low)

    def moveInBounds(self, vert):
        x, y = vert[0], vert[1]
        x = x if x > 0 else 0
        y = y if y > 0 else 0
        x = x if x < self.parent.width else self.parent.width - 1
        y = y if y < self.parent.height else self.parent.height - 1
        return [x, y]

    def moveEdges(self, low=False):
        for edge in self.edges:
            edge.move(low)

    def mergeWithVertex(self, vert):
        self.edges.extend(vert.edges)
        for edge in vert.edges:
            edge.verts[edge.verts.index(vert)] = self
        for edge in self.edges:
            edge.createFace()
        vert.edges = []
        vert.delete()

    def delete(self):
        queue = self.edges[:]
        for edge in queue:
            edge.delete()

        self.parent.mesh.bvertices[int(self.coords[0])][int(self.coords[1])] = 0
        self.parent.mesh.vertices.remove(self)
        self.parent.canvas.delete(self.id)

    def deconnect(self):
        queue = self.edges[:]
        for edge in queue:
            edge.delete()
        self.parent.canvas.delete(self.id)

    def getVisualCoords(self):
        return self.parent.parent.zoom.ToViewport(self.coords)

    def updateIsOuter(self, range=0.001):
        if self.degree < 360 - range:
            self.isOuter = True

    """ EDGE """
    def getEdge(self, vert):
        for edge in self.edges:
            if edge.hasVertex(vert):
                return edge
        return None
