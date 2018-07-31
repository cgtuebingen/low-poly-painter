# TAG
TAG_VERTEX = "v"
TAG_EDGE = "e"
TAG_FACE = "f"

# COLOR
COLOR_DEFAULT = "#000000"

class Face:
    def __init__(self, edge1, edge2, edge3, frame, user=True):
        # Information
        self.id = -1
        self.coords = []
        self.color = COLOR_DEFAULT
        self.edges = (edge1, edge2, edge3)

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
        self.coords = self.getCoordinates(self.getVertices())
        self.color = self.getColorFromImage()
        self.draw()


    """ GENERAL """
    def draw(self, user=True):
        self.id = self.parent.canvas.create_polygon(self.coords[0][0], self.coords[0][1],
                                             self.coords[1][0], self.coords[1][1],
                                             self.coords[2][0], self.coords[2][1],
                                             fill=self.color,
                                             tag=TAG_FACE,
                                             state=self.parent.faceState)
        if (user):
            self.parent.canvas.tag_lower(self.id, TAG_EDGE)

    def getColorFromImage(self):
        return self.parent.color.fromImage(self.coords)

    def move(self):
        self.coords = self.getCoordinates(self.getVertices())
        self.parent.canvas.coords(self.id, self.coords[0][0], self.coords[0][1],
                                           self.coords[1][0], self.coords[1][1],
                                           self.coords[2][0], self.coords[2][1])
        self.color = self.getColorFromImage()
        self.parent.canvas.itemconfig(self.id, fill=self.color)


    def delete(self):
        queue = self.edges[:]
        for edge in queue:
            edge.faces.remove(self)

        self.parent.mesh.faces.remove(self)
        self.parent.canvas.delete(self.id)

    def getVertices(self):
        vert1 = self.edges[0].verts[0].coords
        vert2 = self.edges[0].verts[1].coords
        vert3 = self.edges[1].verts[0].coords
        if vert3 is vert1:
            vert3 = self.edges[1].verts[1].coords
        return [vert1, vert2, vert3]

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
