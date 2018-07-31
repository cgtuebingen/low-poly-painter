# Local Modules
from objects.vertex import Vertex
from objects.edge import Edge
from objects.face import Face

# TAG
TAG_VERTEX = "v"
TAG_EDGE = "e"
TAG_FACE = "f"

class Mesh:
    """
    Canvas Mesh Class

    Description:
    Responsible for the vertices/edges/faces that are drawn on the canvas.
    """

    def __init__(self, parent):
        # Parent
        self.parent = parent

        # Object Arrays
        self.vertices = []
        self.edges = []
        self.faces = []

    """ VERTEX """
    def addVertex(self, coords):
        vert = Vertex(coords, self.parent, self)
        self.vertices.append(vert)
        return vert

    """ EDGE """
    def addEdge(self, vert1, vert2):
        edge = vert1.getEdge(vert2)
        if edge is not None:
            return edge
        edge = Edge(vert1, vert2, self.parent, self)
        self.edges.append(edge)
        return edge

    def getEdgeByID(self, id):
        for edge in self.edges:
            if edge.id == id:
                return edge
        return None

    """ FACE """
    def addFace(self, edge1, edge2, edge3):
        face = Face(edge1, edge2, edge3, self.parent, self)
        self.faces.append(face)
        return face

    def addFaceFromPoints(self, vert1, vert2, vert3):
        edge1 = self.addEdge(vert1, vert2)
        edge2 = self.addEdge(vert1, vert3)
        edge3 = self.addEdge(vert2, vert3)

        faces1 = set(edge1.faces)
        faces2 = set(edge2.faces)
        faces3 = set(edge3.faces)

        # Get the face, all 3 lines have in common
        face = list(faces1 & faces2 & faces3)[0]

        return face

    """ GENERAL """
    def clear(self):
        # Empty arrays
        self.vertices = []
        self.edges = []
        self.faces = []

        # Delete from canvas
        self.parent.canvas.delete(TAG_VERTEX)
        self.parent.canvas.delete(TAG_EDGE)
        self.parent.canvas.delete(TAG_FACE)
        self.parent.selected = None

    """ STORE """
    def save(self):
        vertices = []
        for vertex in self.vertices:
            vertices.append(vertex.coords)

        edges = []
        for edge in self.edges:
            vert1 = self.vertices.index(edge.verts[0])
            vert2 = self.vertices.index(edge.verts[1])
            edges.append([vert1, vert2])

        return [vertices, edges]

    def load(self, meshArray):
        if (meshArray == None):
            return
        vertices = meshArray[0]
        for vertex in vertices:
            self.addVertex(vertex)

        edges = meshArray[1]
        for edge in edges:
            self.addEdge(self.vertices[edge[0]], self.vertices[edge[1]])

    """ FaceSelectingCheck """
    def insideAFace(self, points):
        if not self.faces:
            return [False, None]
        for fa in self.faces:
            if fa.pointInside(points):
               return [True, fa.id]
        return [False, None]
