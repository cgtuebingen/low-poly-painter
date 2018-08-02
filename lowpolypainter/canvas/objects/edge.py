# Local modules
from vertex import Vertex

# TAG
TAG_VERTEX = "v"
TAG_EDGE = "e"
TAG_FACE = "f"

# SIZE
WIDTH = 2

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
        Shift click on Edge: Place vertex on edge
        Default click on vertex: Sets edge as selected
        '''
        self.parent.mouseEvent = True

        if (event.state & MASK_SHIFT):
            vert = self.parent.mesh.addVertex([event.x, event.y])

            # TODO: IF SELECTED IS VERTEX
            if isinstance(self.parent.selected, Vertex):
                self.parent.mesh.addEdge(vert, self.parent.selected)
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

    def draw(self, user=True):
        self.id = self.parent.canvas.create_line(self.verts[0].coords[0],
                                                 self.verts[0].coords[1],
                                                 self.verts[1].coords[0],
                                                 self.verts[1].coords[1],
                                                 tag=TAG_EDGE,
                                                 fill=self.getColor(),
                                                 width=WIDTH)

        self.parent.canvas.tag_bind(self.id, "<Button>", func=self.click)
        if (user):
            self.parent.canvas.tag_lower(self.id, TAG_VERTEX)

    def select(self):
        self.parent.canvas.itemconfigure(self.id, fill=COLOR_SELECTED)
        self.parent.canvas.tag_raise(self.id, TAG_EDGE)

    def deselect(self):
        self.parent.canvas.itemconfigure(self.id, fill=self.getColor())

    def move(self):
        self.parent.canvas.coords(self.id, self.verts[0].coords[0],
                                           self.verts[0].coords[1],
                                           self.verts[1].coords[0],
                                           self.verts[1].coords[1])
         # self.checkValidEdge()
        for face in self.faces:
            face.move()

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

        # if isOnEdge1 and isOnEdge2:
        #    self.parent.addPoint(x1 + s * a, y1 + s * c)

        return isOnEdge1 and isOnEdge2

    def getPossibleIntersectingEdges(self, interpolationSteps = 10):
        """
        Checks rectangles along the path for overlapping Edges on the canvas.
        :param interpolationSteps: Split the rectangle into multiple smaller rectangles.
        :return:
        """
        x1, y1, x2, y2 = self.getCoords()

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
            self.parent.canvas.itemconfigure(self.id, fill=COLOR_DEFAULT)
        else:
            # Invalid Edges should be on top
            self.parent.canvas.tag_raise(self.id, TAG_EDGE)
            self.parent.canvas.itemconfigure(self.id, fill=COLOR_INVALID)

    def addIntersectionWithEdge(self, Edge):
        self.intersectingEdges.add(Edge)
        if len(self.intersectingEdges) == 1:
            self.setValid(False)

    def removeIntersectionWithEdge(self, Edge):
        self.intersectingEdges.remove(Edge)
        if len(self.intersectingEdges) == 0:
            self.setValid(True)

    def getCoords(self):
        x1 = self.verts[0].coords[0]
        x2 = self.verts[1].coords[0]
        y1 = self.verts[0].coords[1]
        y2 = self.verts[1].coords[1]
        return x1, y1, x2, y2
