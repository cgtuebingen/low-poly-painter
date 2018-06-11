from __future__ import division
import collections
import math

from mesh import Vertex

# creates a delaunay triangulation from a set of points saved in a mesh structure,
# using the Bowyer-Watson algorithm
def bowyerWatson(mesh):
    # add super-triangle to mesh
    mesh = addSuperTriangle(mesh)
    # create triangulation by adding vertices pointwise
    for i in range(3,len(mesh.vertices)):
        # triangles which will violate the delaunay-properties after inserting
        badTriangles = []
        # checks each triangle in mesh if it violates the properties
        for j in range(0,len(mesh.faces)):
            triangleCoordinates = [mesh.vertices[mesh.faces[j].vertices[0]],
                                   mesh.vertices[mesh.faces[j].vertices[1]],
                                   mesh.vertices[mesh.faces[j].vertices[2]]]
            # checks if testing-triangle will no longer be valid after inserting
            # a new vertex, by checking if the inserted vertex will be in the circle
            # through the vertices of the triangle
            if isInCircle(mesh.vertices[i], triangleCoordinates):
                badTriangles.append(mesh.faces[j])
        polygon = []
        # find all edges of the invalid triangles that are not shared by any other
        # edges from other invalid triangles
        for j in range(0,len(badTriangles)):
            polygon = notSharedEdges(badTriangles)
        # remove all invalid triangles from resulting mesh
        for j in range(0,len(badTriangles)):
            mesh.faces = remove(badTriangles[j], mesh.faces)
        # adds triangles to mesh that are created by connecting valid edges from invalid triangles
        # with the inserted point
        for j in range(0,len(polygon)):
            mesh.addTriangle(polygon[j][0], polygon[j][1], i)
    # removes all triangles that share at least one vertex with the super-triangle
    mesh = removeSuperVertices(mesh)
    return mesh
          
      
# (!) Temporary Solution
# TODO: add more robust solution
#       solution can fail when having same x coordinate on at least two points
# Checks if a point is within a circle that is constructed by three points
def isInCircle(point, coordinates):
    if coordinates[0].x == coordinates[1].x:
        a = coordinates[0]
        b = coordinates[2]
        c = coordinates[1]
    elif coordinates[1].x == coordinates[2].x:
        a = coordinates[1]
        b = coordinates[0]
        c = coordinates[2]
    else:
        a = coordinates[0]
        b = coordinates[1]
        c = coordinates[2]
    ma = (b.y - a.y) / (b.x - a.x)
    if ma == 0:
        ma = 0.0001
    mb = (c.y - b.y) / (c.x - b.x)
    if mb == 0:
        mb = 0.0001
    if mb - ma == 0:
        ma += 0.0001
    centerX = (ma*mb*(a.y-c.y) + mb * (a.x + b.x) - ma * (b.x + c.x)) / (2 * (mb - ma))
    centerY = (-1 / ma) * (centerX - (a.x + b.x) * 0.5) + (a.y + b.y) * 0.5
    center = Vertex(centerX, centerY)
    radius = euclideanDistance(center,a)
    return radius > euclideanDistance(center,point)


# filters edges that are used multiple times in a list of triangles, by adding all edges
# to a and remove all items that occure at least two times.
def notSharedEdges(badTriangles):
    res = []
    for i in range(0,len(badTriangles)):
        res.append((badTriangles[i].vertices[0], badTriangles[i].vertices[1]))
        res.append((badTriangles[i].vertices[0], badTriangles[i].vertices[2]))
        res.append((badTriangles[i].vertices[1], badTriangles[i].vertices[2]))
    return removeDoubleElements(res)
    

# removes a given triangle from a list of faces
def remove(triangle, faces):
    i = 0
    while i < len(faces):
        if collections.Counter(triangle.vertices) == collections.Counter(faces[i].vertices):
            del faces[i]
        i += 1
    return faces
    

# calculates the euclidean Distance between two points
def euclideanDistance(a,b):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)


# removes all elements in a list of edges that occure more than one time
def removeDoubleElements(edges):
    edges = sorted(edges)
    i = 0
    while i < len(edges):
        j = i+1
        found = False
        while j < len(edges):
            if edges[i] == edges[j]:
                found = True
                del edges[j]
            else:
                j += 1
        if found:
            del edges[i]
        else:
            i += 1
    return edges


# removes the all faces that share at least one vertex with the super-triangle.
# also remove the vertex of the super-triangle from the vertex-list and fixes the vertex indices afterwards
def removeSuperVertices(mesh):
    i = 0
    while i < len(mesh.faces):
        if 0 in mesh.faces[i].vertices or 1 in mesh.faces[i].vertices or 2 in mesh.faces[i].vertices:
            del mesh.faces[i]
        else:
            i += 1
    del mesh.vertices[0]
    del mesh.vertices[0]
    del mesh.vertices[0]
    for i in range(0,len(mesh.faces)):
        mesh.faces[i].vertices = [mesh.faces[i].vertices[0] - 3,
                   mesh.faces[i].vertices[1] - 3,
                   mesh.faces[i].vertices[2] - 3]
    return mesh


# (!) Temporary Solution
# TODO: find a way to generate a super-triangle based on vertices-coordinates
#
# generates a triangle that "should" be large enough to contain all vertices.
def addSuperTriangle(mesh):
    mesh.vertices = [Vertex(-6000,0), 
                     Vertex(6000,0), 
                     Vertex(0,12000)] + mesh.vertices
    mesh.addTriangle(0,1,2)
    return mesh