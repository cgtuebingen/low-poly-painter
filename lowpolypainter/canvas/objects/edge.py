# Local modules
from vertex import Vertex
from lowpolypainter.controlMode import Mode, NUM_RIGHT_CLICK

# TAG
TAG_VERTEX = "v"
TAG_EDGE = "e"
TAG_FACE = "f"

# SIZE
WIDTH = 1
LARGE_WIDTH = 4

# COLOR
COLOR_DEFAULT = "#161616"
COLOR_SELECTED = "#ff0000"
COLOR_INVALID = "#ff7c19"

# MASK
MASK_SHIFT = 0x0001

class Edge:
    def __init__(self, vert1, vert2, frame, user=True):
        # Information
        self.id = -1
        self.faces = []
        self.verts = [vert1, vert2]
        self.intersectingEdges = set()
        self.color = COLOR_DEFAULT

        # Dependencies
        self.parent = frame

        # Update
        vert1.edges.append(self)
        vert2.edges.append(self)

        # User clicked canvas
        if not user:
            return

        # Update
        self.draw()

        # Intersect
        self.checkValidEdge()

        # Face Create
        self.createFace()

    """ EVENTS """
    def click(self, event):
        '''
        Right click on Edge: Place vertex on edge
        Default click on vertex: Sets edge as selected
        '''
        self.parent.mouseEventHandled = True

        if (self.parent.parent.controlMode.mode == Mode.CONNECT_OR_SPLIT) or (event.num == NUM_RIGHT_CLICK):
            self.parent.parent.undoManager.do(self.parent.parent)
            selected = self.parent.selected

            x, y = self.parent.parent.zoom.FromViewport((event.x, event.y))

            vert = self.parent.mesh.addVertex([int(x), int(y)])

            # Split all connected faces in two
            for face in self.faces:
                faceVerts = face.getVertices()
                for faceVert in faceVerts:
                    if not self in faceVert.edges:
                        self.parent.mesh.addEdge(vert, faceVert)

            self.parent.mesh.addEdge(vert, self.verts[0])
            self.parent.mesh.addEdge(vert, self.verts[1])



            self.delete()
        else:
            self.select()
            self.parent.select(self)

    """ GENERAL """
    def getColor(self):
        # calculate gray edge color from rgb values of points in between edge points
        return self.parent.color.grayColorFromImage(self.verts[0], self.verts[1])

    def expand(self, event=None):
        self.parent.canvas.itemconfig(self.id, width=LARGE_WIDTH)

    def shrink(self, event=None):
        self.parent.canvas.itemconfig(self.id, width=WIDTH)

    def draw(self, user=True):
        vertVisualCoords = [self.verts[0].getVisualCoords(), self.verts[1].getVisualCoords()]
        self.color = self.getColor()
        self.id = self.parent.canvas.create_line(vertVisualCoords[0][0],
                                                 vertVisualCoords[0][1],
                                                 vertVisualCoords[1][0],
                                                 vertVisualCoords[1][1],
                                                 tag=TAG_EDGE,
                                                 fill=self.color,
                                                 width=WIDTH,
                                                 state=self.parent.edgesState)

        self.parent.canvas.tag_bind(self.id, "<Button>", func=self.click)
        self.parent.canvas.tag_bind(self.id, sequence="<Enter>", func=self.expand)
        self.parent.canvas.tag_bind(self.id, sequence="<Leave>", func=self.shrink)
        if user:
            self.parent.canvas.tag_lower(self.id, TAG_VERTEX)

    def updatePosition(self):
        vertVisualCoords = [self.verts[0].getVisualCoords(), self.verts[1].getVisualCoords()]
        self.parent.canvas.coords(self.id, vertVisualCoords[0][0],
                                           vertVisualCoords[0][1],
                                           vertVisualCoords[1][0],
                                           vertVisualCoords[1][1])

    def select(self):
        self.parent.canvas.itemconfigure(self.id, fill=COLOR_SELECTED)
        self.parent.canvas.tag_raise(self.id, TAG_EDGE)

    def deselect(self):
        self.parent.canvas.itemconfigure(self.id, fill=self.color)

    def move(self, low=False):
        self.updatePosition()
        if not low:
            self.checkValidEdge()
            self.color = self.getColor()
            self.parent.canvas.itemconfig(self.id, fill=self.color)

        for face in self.faces:
            face.move(low)

    def delete(self):
        queue = self.faces[:]
        for face in queue:
            face.delete()

        queue = self.verts[:]
        for vert in queue:
            vert.edges.remove(self)

        queue = self.intersectingEdges
        for edge in queue:
            edge.removeIntersectionWithEdge(self)

        self.parent.mesh.edges.remove(self)
        self.parent.canvas.delete(self.id)

    """ VERTEX """
    def hasVertex(self, vert):
        return vert in self.verts

    """ FACE """
    def createFace(self):
        '''
        Create face if edges align
        '''
        for edge1 in self.verts[0].edges:
            if edge1 is self:
                continue

            vert = edge1.verts[0]
            if vert is self.verts[0]:
                vert = edge1.verts[1]

            for edge2 in vert.edges:
                if edge2.hasVertex(self.verts[1]):
                    self.parent.mesh.addFace(self, edge1, edge2)

    """ INTERSECT """
    def isIntersectingEdge(self, x3, y3, x4, y4):
        x1, y1, x2, y2 = self.getCoords()

        a = float(x2 - x1)
        b = float(x4 - x3)
        c = float(y2 - y1)
        d = float(y4 - y3)

        s = None
        t = None

        if a == 0 and c == 0:
            # is a Edge of length zero
            t1 = (x1 - x3) / b
            t2 = (y1 - y3) / d
            return t1 == t2
        elif b == 0 and d == 0:
            # is a Edge of length zero
            s1 = (x3 - x1) / a
            s2 = (y3 - y1) / c
            return s1 == s2
        elif a == 0 and b == 0:
            return x1 == x3
        elif c == 0 and d == 0:
            return y1 == y3
        elif a == 0:
            t = (x1 - x3) / b
            s = (y3 - y1 + d * t) / c
        elif b == 0:
            s = (x3 - x1) / a
            t = (y1 - y3 + c * s) / d
        elif c == 0:
            t = (y1 - y3) / d
            s = (x3 - x1 + b * t) / a
        elif d == 0:
            s = (y3 - y1) / c
            t = (x1 - x3 + a * s) / b
        else:
            if (d - c * b / a) != 0:
                t = (y1 + c * x3 / a - c * x1 / a - y3) / (d - c * b / a)
                s = (x3 + b * t - x1) / a
            elif (b - a * d / c) != 0:
                t = (x1 + a * y3 / c - a * y1 / c - x3) / (b - a * d / c)
                s = (x3 + b * t - x1) / a
            elif (c - d * a / b) != 0:
                s = (y3 + d * x1 / b - d * x3 / b - y1) / (c - d * a / b)
                t = (x1 + a * s - x3) / b
            elif (a - b * c / d) != 0:
                s = (x3 + b * y1 / d - b * y3 / d - x1) / (a - b * c / d)
                t = (x1 + a * s - x3) / b

        #print(s, t)

        isOnEdge1 = (s >= 0) and (s <= 1)
        isOnEdge2 = (t >= 0) and (t <= 1)

        return isOnEdge1 and isOnEdge2

    def getPossibleIntersectingEdges(self, interpolationSteps = 10):
        """
        Checks rectangles along the path for overlapping Edges on the canvas.
        :param interpolationSteps: Split the rectangle into multiple smaller rectangles.
        :return:
        """
        x1, y1, x2, y2 = self.getCoords()

        x1, y1 = self.parent.parent.zoom.ToViewport((x1, y1))
        x2, y2 = self.parent.parent.zoom.ToViewport((x2, y2))

        xStep = (x2 - x1) / float(interpolationSteps)
        yStep = (y2 - y1) / float(interpolationSteps)

        overlappingIDs = []

        for i in range(interpolationSteps):
            xRect = x1 + xStep * i
            yRect = y1 + yStep * i
            ids = self.parent.canvas.find_overlapping(xRect, yRect, xRect + xStep, yRect + yStep)
            overlappingIDs += ids

        overlappingIDs = set(overlappingIDs)

        overlappingEdges = []
        for id in overlappingIDs:
            tags = self.parent.canvas.gettags(id)
            if TAG_EDGE in tags:
                overlappingEdges.append(id)

        # remove connected Edges as they cant be intersected
        for vert in self.verts:
            for edge in vert.edges:
                if edge.id in overlappingEdges:
                    overlappingEdges.remove(edge.id)

        return overlappingEdges

    def checkValidEdge(self):
        possibleIDs = self.getPossibleIntersectingEdges()

        currentintersectingEdges = []

        # Check, which Edges actually intersect
        isValid = True
        for id in possibleIDs:
            x3, y3, x4, y4 = self.parent.canvas.coords(id)
            x3, y3 = self.parent.parent.zoom.FromViewport((x3, y3))
            x4, y4 = self.parent.parent.zoom.FromViewport((x4, y4))
            if self.isIntersectingEdge(x3, y3, x4, y4):
                oldEdge = self.parent.mesh.getEdgeByID(id)
                currentintersectingEdges.append(oldEdge)
                isValid = False

        # Check if some Edges stopped intersecting and if yes, notify the other Edge
        # Remove all Edges we already know about from the list
        oldintersectingEdges = self.intersectingEdges.copy()
        for oldEdge in oldintersectingEdges:
            if not oldEdge in currentintersectingEdges:
                self.removeIntersectionWithEdge(oldEdge)
                oldEdge.removeIntersectionWithEdge(self)
            else:
                currentintersectingEdges.remove(oldEdge)

        # Add all Edges that are new to the list of intersecting Edges
        for Edge in currentintersectingEdges:
            self.addIntersectionWithEdge(Edge)
            Edge.addIntersectionWithEdge(self)

        return isValid

    def setValid(self, isValid):
        if isValid:
            self.parent.canvas.itemconfigure(self.id, fill=self.color)
        else:
            # Invalid Edges should be on top
            self.parent.canvas.tag_raise(self.id, TAG_EDGE)
            self.parent.canvas.itemconfigure(self.id, fill=COLOR_INVALID)

    def addIntersectionWithEdge(self, edge):
        self.intersectingEdges.add(edge)
        if len(self.intersectingEdges) == 1:
            self.setValid(False)

    def removeIntersectionWithEdge(self, edge):
        self.intersectingEdges.remove(edge)
        if len(self.intersectingEdges) == 0:
            self.setValid(True)

    def getCoords(self):
        x1 = self.verts[0].coords[0]
        x2 = self.verts[1].coords[0]
        y1 = self.verts[0].coords[1]
        y2 = self.verts[1].coords[1]
        return x1, y1, x2, y2
