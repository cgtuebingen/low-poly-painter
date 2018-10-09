import numpy as np
from lowpolypainter.controlMode import Mode, NUM_MIDDLE_CLICK

# TAG
TAG_VERTEX = "v"
TAG_EDGE = "e"
TAG_FACE = "f"

# COLOR
COLOR_DEFAULT = "#000000"
COLOR_SELECTED = "#ff0000"

# Masks
ALT_MASK = 0x131072

class Face:
    def __init__(self, edge1, edge2, edge3, frame, user=True):
        # Information
        self.id = -1
        self.coords = []
        self.color = COLOR_DEFAULT
        self.edges = (edge1, edge2, edge3)
        self.colorLock = False
        self.IsCustomColored = False

        # Update
        edge1.faces.append(self)
        edge2.faces.append(self)
        edge3.faces.append(self)

        # Dependencies
        self.parent = frame

        # User clicked canvas
        if not user:
            return

        # Update
        self.coords = self.getCoordinates(self.getVerticesCoords())
        self.color = self.getColorFromImage()
        self.draw()


    """ GENERAL """
    def draw(self, user=True):
        vertVisualCoords = [self.parent.parent.zoom.ToViewport(self.coords[0]),
                            self.parent.parent.zoom.ToViewport(self.coords[1]),
                            self.parent.parent.zoom.ToViewport(self.coords[2])]
        self.id = self.parent.canvas.create_polygon(vertVisualCoords[0][0],
                                                    vertVisualCoords[0][1],
                                                    vertVisualCoords[1][0],
                                                    vertVisualCoords[1][1],
                                                    vertVisualCoords[2][0],
                                                    vertVisualCoords[2][1],
                                                    fill=self.color,
                                                    tag=TAG_FACE,
                                                    state=self.parent.faceState)
        self.parent.canvas.tag_bind(self.id, "<Button>", func=self.click)

        if user:
            self.parent.canvas.tag_lower(self.id, TAG_EDGE)

    def updatePosition(self):
        self.coords = self.getCoordinates(self.getVerticesCoords())
        vertVisualCoords = [self.parent.parent.zoom.ToViewport(self.coords[0]),
                            self.parent.parent.zoom.ToViewport(self.coords[1]),
                            self.parent.parent.zoom.ToViewport(self.coords[2])]
        self.parent.canvas.coords(self.id, vertVisualCoords[0][0],
                                           vertVisualCoords[0][1],
                                           vertVisualCoords[1][0],
                                           vertVisualCoords[1][1],
                                           vertVisualCoords[2][0],
                                           vertVisualCoords[2][1])

    def getColorFromImage(self):
        return self.parent.color.fromImage(self.coords)

    def setColor(self, color):
        self.colorLock = True
        self.color = color
        # Recolor
        self.parent.canvas.itemconfig(self.id, fill=self.color)

    def move(self, low=False):
        self.updatePosition()
        if not self.colorLock and not low:
            self.color = self.getColorFromImage()

        self.parent.canvas.itemconfig(self.id, fill=self.color)

    def delete(self):
        queue = self.edges[:]
        for edge in queue:
            edge.faces.remove(self)

        self.parent.mesh.faces.remove(self)
        self.parent.canvas.delete(self.id)

    def getVerticesCoords(self):
        vert1 = self.edges[0].verts[0].coords
        vert2 = self.edges[0].verts[1].coords
        vert3 = self.edges[1].verts[0].coords
        if vert3 is vert1 or vert3 is vert2:
            vert3 = self.edges[1].verts[1].coords
        return [vert1, vert2, vert3]

    def getVertices(self):
        vert1 = self.edges[0].verts[0]
        vert2 = self.edges[0].verts[1]
        vert3 = self.edges[1].verts[0]
        if vert3 is vert1 or vert3 is vert2:
            vert3 = self.edges[1].verts[1]
        return [vert1, vert2, vert3]
    # what is happening here?
    def getCoordinates(self, verts):
        verts.sort(key = lambda vert: vert[1], reverse = False)
        if verts[0][1] == verts[1][1]:
            if verts[0][0] < verts[1][0]:
                verts[0], verts[1] = verts[1], verts[0]

        rot = (verts[1][1] - verts[0][1])*(verts[2][0] - verts[1][0])
        ate = (verts[2][1] - verts[1][1])*(verts[1][0] - verts[0][0])
        rotate = rot - ate

        if rotate < 0:
            verts[1], verts[2] = verts[2], verts[1]

        return verts

    # New faceselection Method
    def click(self, event):
        # Selection on click for coloring
        # Deselection by clicking on empty canvas or clicking again

        self.parent.mouseEventHandled = True
        if self.parent.parent.controlMode.mode == Mode.BUCKET:
            self.parent.parent.undoManager.do(self.parent.parent)
            rgb, hsv, hexa = self.parent.parent.detailFrame.colorpicker.square.get()
            if self.parent.parent.detailFrame.colorpicker.alpha_channel:
                hexa = self.parent.parent.detailFrame.colorpicker.hexa.get()
                rgb += (self.parent.parent.detailFrame.colorpicker.alpha.get(),)
            self.parent.parent.detailFrame.colorpicker.color  = rgb, hsv, hexa
            self.setColor(hexa)
            self.IsCustomColored = True







    def select(self):
        for edge in self.edges:
            self.parent.canvas.itemconfigure(edge.id, fill=COLOR_SELECTED)
            self.parent.canvas.tag_raise(edge.id, TAG_EDGE)

    def deselect(self):
        for edge in self.edges:
            self.parent.canvas.itemconfigure(edge.id, fill=edge.color)

    # Not in use
    # Calculate if a given point is inside the current face
    # Using a given a rectangle as raw approximation and barycentric coordinates for fine tuning.
    def pointInside(self, point):
        coords = self.getCoordinates(self.getVerticesCoords())
        if (coords[0][0]>point[0] and coords[1][0]>point[0] and coords[2][0]>point[0]):
            return False
        if (coords[0][0]<point[0] and coords[1][0]<point[0] and coords[2][0]<point[0]):
            return False
        if (coords[0][1] > point[1] and coords[1][1] > point[1] and coords[2][1] > point[1]):
            return False
        if (coords[0][1] < point[1] and coords[1][1] < point[1] and coords[2][1] < point[1]):
            return False
        else:
            if float(float(float(coords[1][1] - coords[2][1]) * float(coords[0][0] - coords[2][0])) + float(float(coords[2][0] - coords[1][0]) * float(coords[0][1] - coords[2][1])))==0:
                return False
            if float(float(float(coords[1][1] - coords[2][1]) * float(coords[0][0] - coords[2][0])) + float(float(coords[2][0] - coords[1][0]) * float(coords[0][1] - coords[2][1])))==0:
                return False
            alpha = float(float(float(float(coords[1][1] - coords[2][1]) * float(point[0] - coords[2][0])) + float(float(coords[2][0] - coords[1][0]) * float(point[1] - coords[2][1]))) / float(float(float(coords[1][1] - coords[2][1]) * float(coords[0][0] - coords[2][0])) + float(float(coords[2][0] - coords[1][0]) * float(coords[0][1] - coords[2][1]))))
            beta = float(float(float(float(coords[2][1] - coords[0][1]) * float(point[0] - coords[2][0])) + float(float(coords[0][0] - coords[2][0]) * float(point[1] - coords[2][1]))) / float(float(float(coords[1][1] - coords[2][1]) * float(coords[0][0] - coords[2][0])) + float(float(coords[2][0] - coords[1][0]) * float(coords[0][1] - coords[2][1]))))
            gamma = float(float(float(1.0)-float(alpha)-float(beta)))
            if((float(alpha)>float(0))and(float(beta)>float(0))and(float(gamma)>float(0))):
                return True
            else:
                return False

    # Not in use
    # Calculate degree for connected vertices
    def calcVerticesDegrees(self):
        verts = self.getVertices()
        # points
        A = np.array((verts[0].coords[0], verts[0].coords[1]))
        B = np.array((verts[1].coords[0], verts[1].coords[1]))
        C = np.array((verts[2].coords[0], verts[2].coords[1]))

        # lines
        a = np.linalg.norm(B-C)
        b = np.linalg.norm(A-C)
        c = np.linalg.norm(A-B)

        # degrees
        alpha = np.degrees(np.arccos( (a**2 - b**2 - c**2) / (-2*b*c) ))
        beta = np.degrees(np.arccos( (b**2 - a**2 - c**2) / (-2*a*c) ))
        gamma = np.degrees(np.arccos( (c**2 - a**2 - b**2) / (-2*a*b) ))

        # Removed degree from vertex
        # verts[0].degree += alpha
        # verts[1].degree += beta
        # verts[2].degree += gamma
