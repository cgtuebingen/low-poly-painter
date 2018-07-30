# TAG
TAG_VERTEX = "v"
TAG_EDGE = "e"
TAG_FACE = "f"

# SIZE
RADIUS = 4

# COLOR
COLOR_DEFAULT = "#0000ff"
COLOR_SELECTED = "#ff0000"

# MASK
MASK_SHIFT = 0x0001

class Vertex:
    """
    Vertex

    Functions:
    Handels Vetex creation, movement, selection and updating
    """

    def __init__(self, coords, frame, mesh):
        # Information
        self.id = -1
        self.coords = coords

        # Part of edges
        self.edges = []

        # Dependencies
        self.mesh = mesh
        self.frame = frame
        self.canvas = frame.canvas

        # Update
        self.draw()
        self.select()
        self.frame.select(self)

    """ EVENTS """
    def clickHandle(self, event):
        '''
        Shift click on vertex: Creates edge to vertex
        Default click on vertex: Sets vertex as selected
        '''
        self.frame.mouseEvent = True
        if (event.state & MASK_SHIFT) and (self.frame.selected is not None):
            self.mesh.addEdge(self, self.frame.selected)
            return
        self.select()
        self.frame.select(self)

    def moveHandle(self, event):
        self.move(self.moveInBounds([event.x, event.y]))

    def releaseHandle(self, event):
        self.frame.mouseEvent = False

    """ GENERAL """
    def draw(self):
        self.id = self.canvas.create_oval(self.coords[0] - RADIUS,
                                          self.coords[1] - RADIUS,
                                          self.coords[0] + RADIUS,
                                          self.coords[1] + RADIUS,
                                          fill = COLOR_DEFAULT,
                                          tag = TAG_VERTEX)

        self.canvas.tag_bind(self.id, sequence="<Button>", func=self.clickHandle)
        self.canvas.tag_bind(self.id, sequence="<B1-Motion>", func=self.moveHandle)
        self.canvas.tag_bind(self.id, sequence="<ButtonRelease-1>", func=self.releaseHandle)

    def select(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_SELECTED)
        self.canvas.tag_raise(self.id, TAG_VERTEX)

    def deselect(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_DEFAULT)

    def move(self, vert):
        moveVert = [vert[0] - self.coords[0], vert[1] - self.coords[1]]
        self.canvas.move(self.id, moveVert[0], moveVert[1])
        self.coords = vert
        self.moveEdges()

    def moveInBounds(self, vert):
        x, y = vert[0], vert[1]
        x = x if x > 0 else 0
        y = y if y > 0 else 0
        x = x if x <= self.frame.width else self.frame.width - 1
        y = y if y <= self.frame.height else self.frame.height - 1
        return [x, y]

    def moveEdges(self):
        for edge in self.edges:
            edge.move()

    def delete(self):
        queue = self.edges[:]
        for edge in queue:
            edge.delete()

        self.mesh.vertices.remove(self)
        self.canvas.delete(self.id)


    """ EDGE """
    def getEdge(self, vert):
        for edge in self.edges:
            if edge.hasVertex(vert):
                return edge
        return None
