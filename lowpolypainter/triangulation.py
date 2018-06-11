from __future__ import division
import collections
import math

from mesh import Vertex, Face

"""auxiliary procedures
"""

"""
Circle Class

Description: Circle defind by center point and radius
"""

class Circle(object):
    def __init__(self, middle, radius):
        self.middle = middle
        self.radius = radius
    
    #checks if point is in circle area
    def check(self, point):
        return(self.middle.distance(point)<=self.radius)
        
"""
Vector Class

Description: Vector with base "point" and direction (x/y)
"""

class Vector(object):
    def __init__(self, point, x, y):
        self.point = point
        self.x = x
        self.y = y
    
    #TODO: find a more elegant solution
    #finds intersection of two vectors
    def findIntersection(self, line):
        x1 = self.point.x
        x2 = line.point.x
        y1 = self.point.y
        y2 = line.point.y
        c = self.x
        d = self.y
        e = line.x
        f = line.y
        if(self.parallel(line)):
            return False
        else:
            if(c==0):
                b = (float(x1-x2)/e)
                result = Vertex(x2+b*e, y2+b*f)
            else:
                if(e==0):
                    a = float(x2-x1)/c
                    result = Vertex(x1+a*c, y1+a*d)
                else:
                    if(d==0):
                        b = float(y1-y2)/f
                        result = Vertex(x1+b*e, y2+b*f)
                    else:
                        if(f==0):
                            a = float(y2-y1)/d
                            result = Vertex(x1+a*c, y1+a*d)
                        else:
                            if((float(c*f)/d)==e):
                                a = float(x2+(float(y1-y2)/f)*e-x1)/(c-float(d*e)/f)
                                result = Vertex(x1+a*c, y1+a*d)
                            else:
                                b = float(x1+(float(y2-y1)/d)*c-x2)/(e-float(c*f)/d)
                                result = Vertex(x2+b*e, y2+b*f)
        return result
    
    #checks if two vectors are parallels
    def parallel(self, line):
        x1 = self.x
        x2 = self.y
        y1 = line.x
        y2 = line.y
        return ((x1 == y1 == 0) 
                or (x2 == y2 == 0) 
                or (x1 != 0 and y1 != 0 and float(x2)/x1 == float(y2)/y1) 
                or (x2 != 0 and y2 != 0 and float(x1)/x2 == float(y1)/y2)
                or (x1 == x2 == 0)
                or (y1 == y2 == 0))

"""
Face Class
Description: expands Face Class

"""
class Face(Face):
    def __init__(self, vertexPos1, vertexPos2, vertexPos3, color):
        self.vertices = [vertexPos1, vertexPos2, vertexPos3]
        self.color = color
        self.circle = self.findCircle()
    
    #circle containing the three vertices of the triangle
    def findCircle(self):
        x1 = self.vertices[0]
        x2 = self.vertices[1]
        x3 = self.vertices[2]
        line1 = x1.mid(x2)
        line2 = x1.mid(x3)
        intersection = line1.findIntersection(line2)
        radius = intersection.distance(x1)
        circle = Circle(intersection, radius)
        return circle

"""
Vertex Class
Description: expands Vertex Class
"""
class Vertex(Vertex):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    #distance of two vertices
    def distance(self, point):
        return ((self.x - point.x)**2 + (self.y - point.y)**2)**(float(1)/2)
    
    #median
    def mid(self, point):
        a = self.x - point.x
        b = self.y - point.y
        middle = Vertex(float(self.x + point.x)/2,float(self.y + point.y)/2)
        return Vector(middle, b, a)
    
    #vector running through two given points
    def drawLine(self, point):
        x1 = self.x
        y1 = self.y
        x2 = point.x
        y2 = point.y
        return Vector(self, x2-x1, y2-y1)

"""
Delaunay triangulation starts here
"""

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
          
      
# Checks if a point is within a circle that is constructed by three points
def isInCircle(point, coordinates):
    face = Face(coordinates[0], coordinates[1], coordinates[2], 0)
    return face.circle.check(point)


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
