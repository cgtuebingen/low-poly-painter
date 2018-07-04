# TODO: Add better function to insert new faces
# TODO: Delete vertecies or faces one by one

from operator import attrgetter

"""
Mesh Class

Description:
Stores mesh of vertices, which connections are stored as faces.
Points and tris can be added and removed from the mesh.
"""

class Mesh(object):

    def __init__(self, width, height):
        self.faces = []
        self.edges = []
        self.vertices = []
        self.width = width
        self.height = height

    # Adds vertex to mesh
    def addVertex(self, x, y):
        # Create Vertex
        vertex = Vertex(x, y)
        self.vertices.append(vertex)
        return len(self.vertices) - 1

    # Adds edge to mesh
    def addEdge(self, vertexIndex1, vertexIndex2):
        # Create Edge
        edge = Edge(vertexIndex1, vertexIndex2)
        self.edges.append(edge)

    # Adds face to mesh
    # (!) Rotates faces anticlockwise
    def addFace(self, vertexIndex1, vertexIndex2, vertexIndex3, color):

        # Sort array by y value
        verticesIndex = [vertexIndex1, vertexIndex2, vertexIndex3]
        verticesIndex.sort(key = lambda i: self.vertices[i].y, reverse = False)

        # Current vertices sorted by y
        v1 = self.vertices[verticesIndex[0]]
        v2 = self.vertices[verticesIndex[1]]
        v3 = self.vertices[verticesIndex[2]]

        if v1.y == v2.y:
            if v1.x < v2.x:
                v1, v2 = v2, v1
                verticesIndex[0], verticesIndex[1] = verticesIndex[1], verticesIndex[0]

        # Calculate winding order
        rotation = (v2.y - v1.y)*(v3.x - v2.x) - (v3.y - v2.y)*(v2.x - v1.x)

        if rotation < 0:
            verticesIndex[1], verticesIndex[2] = verticesIndex[2], verticesIndex[1]

        # Create face when value isn't collinear
        face = Face(verticesIndex[0], verticesIndex[1], verticesIndex[2], color)
        self.faces.append(face)


    # Deletes all vertecies and faces
    def clear(self):
        self.faces = []
        self.edges = []
        self.vertices = []


"""
Vertex Class

Description:
Stores a vertex of the mesh, which contains and x and y coordinate.
"""

class Vertex(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

"""
Edge Class

Description:
Stores a edge of the mesh, which contains two vertecies
"""

class Edge(object):

    def __init__(self, vertexPos1, vertexPos2):
        self.vertices = [vertexPos1, vertexPos2]


"""
Face Class

Description:
Stores faces of the mesh, which contains three vertecies and a color.
"""

class Face(object):

    def __init__(self, vertexPos1, vertexPos2, vertexPos3, color):
        self.vertices = [vertexPos1, vertexPos2, vertexPos3]
        self.color = color
