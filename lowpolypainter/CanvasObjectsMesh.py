from CanvasObjects import *
from mesh import Mesh


class CanvasObjectsMesh:
    """
    This class is responsible for the points/lines/faces that are drawn on the canvas.
    """

    def __init__(self, gui):
        self.gui = gui

        self.points = []
        self.lines = []
        self.faces = []

    def addFace(self, line1, line2, line3):
        face = CanvasFace(line1, line2, line3, self.gui, self)
        self.faces.append(face)
        return face

    def addFaceFromPoints(self, point1, point2, point3):
        # addLine checks if they already exist
        line1 = self.addLine(point1, point2)
        line2 = self.addLine(point1, point3)
        line3 = self.addLine(point2, point3)

        faces1 = set(line1.faces)
        faces2 = set(line2.faces)
        faces3 = set(line3.faces)

        # Get the face, all 3 lines have in common
        face = list(faces1 & faces2 & faces3)[0]

        return face

    def addLine(self, point1, point2):
        # Check if line to selected point already exists
        line = point1.getConnectingLine(point2)
        if line is not None:
            return line

        line = CanvasLine(point1, point2, self.gui, self)
        self.lines.append(line)
        return line

    def addPoint(self, x, y):
        point = CanvasPoint(x, y, self.gui, self)
        self.points.append(point)
        return point

    def toMesh(self):
        mesh = Mesh(self.gui.frameWidth, self.gui.frameHeight)
        pointIndices = []

        # Add all vertices
        for point in self.points:
            i = mesh.addVertex(point.x, point.y)
            pointIndices.append(i)

        # Add all lines
        for line in self.lines:
            point1 = line.points[0]
            point2 = line.points[1]

            i1 = pointIndices[self.points.index(point1)]
            i2 = pointIndices[self.points.index(point2)]

            mesh.addEdge(i1, i2)

        # Add all faces
        for face in self.faces:
            points = face.getPoints()
            i1 = pointIndices[self.points.index(points[0])]
            i2 = pointIndices[self.points.index(points[1])]
            i3 = pointIndices[self.points.index(points[2])]

            face.getAutoColor()

            mesh.addFace(i1, i2, i3, face.color)

        print(len(mesh.vertices), len(mesh.edges), len(mesh.faces))

        return mesh

    def fromMesh(self, mesh):
        self.clear()

        # Points
        for point in mesh.vertices:
            self.addPoint(point.x, point.y)

        # Lines
        for line in mesh.edges:
            self.addLine(self.points[line.vertices[0]], self.points[line.vertices[1]])

        # if the edges of the face where not in the edges list, then add them now
        for face in mesh.faces:
            points = []
            for i in range(3):
                points.append(self.points[face.vertices[i]])

            # Check that all lines of the face are there and if not, then create them
            # This check is performed in the addLine method
            for i, j in [(0, 1), (1, 2), (2, 0)]:
                self.addLine(points[i], points[j])

    def clear(self):
        # Empty the lists
        self.points = []
        self.lines = []
        self.faces = []

        # Delete from canvas
        self.gui.canvas.delete(TAG_POINT)
        self.gui.canvas.delete(TAG_LINE)
        self.gui.canvas.delete(TAG_FACE)

        self.gui.selectedPoint = None
