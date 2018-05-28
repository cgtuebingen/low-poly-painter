# TODO: Add better function to insert new faces
# TODO: Delete vertecies or faces one by one

"""
Mesh Class

Description:
Stores mesh of vertices, which connections are stored as faces.
Points and tris can be added and removed from the mesh.
"""

class Mesh(object):

    def __init__(self, width, height):
        self.faces = []
        self.vertices = []
        self.width = width
        self.height = height

    # Adds vertex to mesh
    def addVertex(self, x, y):
        vertex = Vertex(x, y)
        self.vertices.append(vertex)

    # Adds face to mesh
    def addFace(self, vertexIndex1, vertexIndex2, vertexIndex3, color):
        face = Face(vertexIndex1, vertexIndex2, vertexIndex3, color)
        self.faces.append(face)

    # Deletes all vertecies and faces
    def clear(self):
        self.faces = []
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
Face Class

Description:
Stores faces of the mesh, which contains three vertecies and a color.
"""

class Face(object):

    def __init__(self, vertexPos1, vertexPos2, vertexPos3, color):
        self.vertices = [vertexPos1, vertexPos2, vertexPos3]
        self.color = color
