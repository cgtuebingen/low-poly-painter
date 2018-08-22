# Python Modules
import numpy as np
import time
import copy

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

        # Image Vertices Array
        self.bvertices = np.zeros([self.parent.width, self.parent.height]).tolist()

    def updatePositions(self):
        for vertex in self.vertices:
            vertex.updatePosition()
        for edge in self.edges:
            edge.updatePosition()
        for face in self.faces:
            face.updatePosition()

    """ VERTEX """
    def addVertex(self, coords):
        vert = Vertex(coords, self.parent)
        self.bvertices[int(coords[0])][int(coords[1])] = vert
        self.vertices.append(vert)
        return vert

    """ EDGE """
    def addEdge(self, vert1, vert2):
        edge = vert1.getEdge(vert2)
        if edge is not None:
            return edge
        edge = Edge(vert1, vert2, self.parent)
        self.edges.append(edge)
        return edge

    def getEdgeByID(self, id):
        for edge in self.edges:
            if edge.id == id:
                return edge
        return None

    """ FACE """
    def addFace(self, edge1, edge2, edge3):
        face = Face(edge1, edge2, edge3, self.parent)
        self.faces.append(face)
        return face

    def getFaceByID(self, id):
        for face in self.faces:
            if face.id == id:
                return face
        return None

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


    def faceToVertexGeneration(self, point1, point2, point3):
        # Fast way to generate given face by points
        # Starts at face and generates edges and vertices
        # Init methodes are not used as they should be used
        # (!) Point should be array of coordinate

        # Vertecies
        vert1 = self.bvertices[point1[0]][point1[1]]
        if vert1 == 0:
            vert1 = Vertex(point1, self.parent, False)
            self.bvertices[point1[0]][point1[1]] = vert1
            self.vertices.append(vert1)

        vert2 = self.bvertices[point2[0]][point2[1]]
        if vert2 == 0:
            vert2 = Vertex(point2, self.parent, False)
            self.bvertices[point2[0]][point2[1]] = vert2
            self.vertices.append(vert2)

        vert3 = self.bvertices[point3[0]][point3[1]]
        if vert3 == 0:
            vert3 = Vertex(point3, self.parent, False)
            self.bvertices[point3[0]][point3[1]] = vert3
            self.vertices.append(vert3)

        # Edges
        edge1 = vert1.getEdge(vert2)
        if (edge1 == None ):
            edge1 = Edge(vert1, vert2, self.parent, False)
            self.edges.append(edge1)

        edge2 = vert2.getEdge(vert3)
        if (edge2 == None ):
            edge2 = Edge(vert2, vert3, self.parent, False)
            self.edges.append(edge2)

        edge3 = vert3.getEdge(vert1)
        if (edge3 == None ):
            edge3 = Edge(vert3, vert1, self.parent, False)
            self.edges.append(edge3)

        # Face
        face = Face(edge1, edge2, edge3, self.parent, False)
        face.coords = face.getCoordinates([point1, point2, point3])
        face.color = face.getColorFromImage()
        self.faces.append(face)

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
    
    # saves current mesh.
    # differs from "save" because edges will not get saved with indices of their vertices
    def save1(self):
        vertices = map(lambda x: x.coords, self.vertices)
        edges = map(lambda x: [x.verts[0].coords, x.verts[1].coords], self.edges)
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
            
    def load1(self, meshArray):
        if (meshArray == None):
            return
        vertices = meshArray[0]
        for vertex in vertices:
            self.addVertex(vertex)
        edges = meshArray[1]
        for edge in edges:
            self.addEdge(self.getVertexByCoords(edge[0]), self.getVertexByCoords(edge[1]))
            
    def getVertexByCoords(self, coordinates):
        for vertex in self.vertices:
            if vertex.coords == coordinates:
                return vertex


    # Unused but keeping it as an alternative for now.
    def insideAFace(self, points):
        if not self.faces:
            return [False, None]
        for fa in self.faces:
            if fa.pointInside(points):
                return [True, fa.id]
        print(end - start)
        return [False, None]
