# Python modules
from operator import attrgetter

# Local modules
from lowpolypainter.color import Color

TAG_POINT = "point"
TAG_LINE = "line"
TAG_FACE = "face"
COLOR_POINT_DEFAULT = "#0000ff"
COLOR_POINT_SELECTED = "#ff0000"
COLOR_LINE_DEFAULT = "#000"
COLOR_LINE_SELECTED = "#ff0000"


class CanvasPoint:
    """
    CanvasPoint

    This class handles the creation, movement, selection and updating of points and their connected lines.
    It contains the event handlers
    """
    RADIUS = 4

    def __init__(self, x, y, canvasFrame):
        self.x = x
        self.y = y

        self.canvas = canvasFrame.canvas
        self.canvasFrame = canvasFrame

        # Stores all lines that use this point
        # This way an update to the point can also update these lines
        self.connectedLines = []

        self.id = -1
        self.draw()

        self.canvasFrame.selectPoint(self)

        self.moved = False

    def click(self, event):
        # Click to select point or shift-click to connect to this point
        shiftMask = 0x0001
        self.canvasFrame.mouseEventHandled = True
        if (event.state & shiftMask) and (self.canvasFrame.selectedPoint is not None):
            self.canvasFrame.addLine(self, self.canvasFrame.selectedPoint)
            return
        self.canvasFrame.selectPoint(self)

    def draw(self):
        # Delete old
        if self.id != -1:
            self.canvas.delete(self.id)

        radius = CanvasPoint.RADIUS
        self.id = self.canvas.create_oval(self.x - radius,
                                          self.y - radius,
                                          self.x + radius,
                                          self.y + radius,
                                          fill=COLOR_POINT_DEFAULT,
                                          tag=TAG_POINT)

        # Event handlers have to be rebound if the point is redrawn
        self.canvas.tag_bind(self.id, sequence="<Button>", func=self.click)
        self.canvas.tag_bind(self.id, sequence="<B1-Motion>", func=self.move)
        self.canvas.tag_bind(self.id, sequence="<ButtonRelease-1>", func=self.finalizeMove)

    def select(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_POINT_SELECTED)
        self.canvas.tag_raise(self.id, TAG_POINT)

    def deactivate(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_POINT_DEFAULT)

    def move(self, event):
        x = event.x
        y = event.y

        # Confine coordinates to image size
        if x < 0:
            x = 0
        elif x >= self.canvasFrame.frameWidth:
            x = self.canvasFrame.frameWidth - 1

        if y < 0:
            y = 0
        elif y >= self.canvasFrame.frameWidth:
            y = self.canvasFrame.frameWidth - 1

        self.moved = True
        self.canvas.move(self.id, x - self.x, y - self.y)

        self.x = x
        self.y = y

        for line in self.connectedLines:
            line.update()

    def finalizeMove(self, event):
        """
        A moved point, and therefore often moved lines and faces, should not recalculate the color of the face
        for each movement but only once after the movement ended.
        :param event:
        :return:
        """
        if self.moved:
            for line in self.connectedLines:
                line.update(recalcColor=True)
        self.moved = False

    def hasConnectingLine(self, point):
        """
        Check if any connected line connects to point.
        :param point:
        :return:
        """
        for line in self.connectedLines:
            if line.isConnectedTo(point):
                return True
        return False

    def delete(self):
        self.canvasFrame.points.remove(self)
        self.canvas.delete(self.id)

        # All lines that use this point, have to be deleted
        # Copy the list, because deleting a line removes it from the connectedLines list
        deleteQueue = self.connectedLines[:]
        for line in deleteQueue:
            line.delete()


class CanvasLine:
    def __init__(self, canvasPoint1, canvasPoint2, canvasFrame):
        # The two line points
        self.points = (canvasPoint1, canvasPoint2)

        # Set references to this line in points
        canvasPoint1.connectedLines.append(self)
        canvasPoint2.connectedLines.append(self)

        self.canvas = canvasFrame.canvas
        self.canvasFrame = canvasFrame

        self.id = -1
        self.draw()

        # Stores all faces that use this line
        # This way an update to this line can also update all dependent faces
        self.faces = []

        # A new line could create a face
        self.checkFaceCreated()

        self.deleted = False

    def click(self, event):
        shiftMask = 0x0001
        self.canvasFrame.mouseEventHandled = True

        selectedPoint = self.canvasFrame.selectedPoint

        # Press shift to place points on lines
        # Automatically splits line and adds the 2 or 3 lines
        if event.state & shiftMask:
            point = self.canvasFrame.addPoint(event.x, event.y)

            # If there is a selected point, then also add a line to it
            if selectedPoint is not None:
                self.canvasFrame.addLine(point, selectedPoint)
            self.canvasFrame.addLine(point, self.points[0])
            self.canvasFrame.addLine(point, self.points[1])

            self.delete()
        else:
            self.canvasFrame.selectLine(self)

    def checkFaceCreated(self):
        """
        If an added line creates a triangle, then add the corresponding face.
        :return:
        """

        # Checks if one point of this line can be reached over 2 connected lines from the other point
        for line1 in self.points[0].connectedLines:
            if line1 is self:
                continue

            point = line1.points[0]
            if point is self.points[0]:
                point = line1.points[1]

            for line2 in point.connectedLines:
                if line2.isConnectedTo(self.points[1]):
                    self.canvasFrame.addFace(self, line1, line2)

    def select(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_LINE_SELECTED)
        self.canvas.tag_raise(self.id, TAG_LINE)

    def deactivate(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_LINE_DEFAULT)

    def draw(self):
        # Delete old
        if self.id != -1:
            self.canvas.delete(self.id)

        self.id = self.canvas.create_line(self.points[0].x, self.points[0].y,
                                          self.points[1].x, self.points[1].y,
                                          tag=TAG_LINE,
                                          fill=COLOR_LINE_DEFAULT,
                                          width=4)

        # Bind mouse click event
        self.canvas.tag_bind(self.id, "<Button>", func=self.click)

        # Lines should all be below points
        self.canvas.tag_lower(self.id, TAG_POINT)

    def update(self, recalcColor=False):
        self.draw()

        for face in self.faces:
            face.update(recalcColor)

    def isConnectedTo(self, point):
        return point in self.points

    def delete(self):
        if not self.deleted:
            self.canvasFrame.lines.remove(self)
            self.canvas.delete(self.id)

            deleteQueue = self.faces[:]
            for face in deleteQueue:
                face.delete()
            for point in self.points:
                point.connectedLines.remove(self)

        self.deleted = True


class CanvasFace:
    def __init__(self, line1, line2, line3, canvasFrame):
        # Lines
        self.lines = (line1, line2, line3)

        self.canvas = canvasFrame.canvas
        self.canvasFrame = canvasFrame

        self.color = "#000"
        self.getAutoColor()

        self.id = -1
        self.draw()

        # Add reference to all 3 lines
        for line in self.lines:
            line.faces.append(self)

        self.deleted = False

    def draw(self):
        # Delete old
        if self.id != -1:
            self.canvas.delete(self.id)

        coords = self.getCoordinates()

        self.id = self.canvas.create_polygon(coords[0][0], coords[0][1],
                                             coords[1][0], coords[1][1],
                                             coords[2][0], coords[2][1],
                                             fill=self.color,
                                             tag=TAG_FACE,
                                             state=self.canvasFrame.currentFaceState)

        # Faces should be below lines and points
        self.canvas.tag_lower(self.id, TAG_LINE)

    def getAutoColor(self):
        """
        Calculates color based on the pixels of the image below this face
        :return:
        """
        coords = self.getCoordinates()
        self.color = Color.fromImage(self.canvasFrame.image, 1, coords)

    def update(self, recalcColor):
        if recalcColor:
            self.getAutoColor()
        self.draw()

    def delete(self):
        if not self.deleted:
            self.canvasFrame.faces.remove(self)
            self.canvas.delete(self.id)
            for line in self.lines:
                line.faces.remove(self)

        self.deleted = True

    def getPoints(self):
        # Get all points from lines
        point1 = self.lines[0].points[0]
        point2 = self.lines[0].points[1]
        point3 = self.lines[1].points[0]
        if point3 is point1:
            point3 = self.lines[1].points[1]

        points = [point1, point2, point3]
        return points

    def getCoordinates(self):
        """
        Get the coordinates of the corners in anti-clockwise order.
        :return:
        """
        points = self.getPoints()
        yxSorted = sorted(points, key=attrgetter("y", "x"))

        # Current vertices sorted by y
        v1 = yxSorted[0]
        v2 = yxSorted[1]
        v3 = yxSorted[2]

        # Calculate slope for v2 and v3 to v1
        mv2v1 = (v2.x - v1.x) / float(v2.y - v1.y) if (v2.y - v1.y) != 0 else 0
        mv3v1 = (v3.x - v1.x) / float(v3.y - v1.y) if (v3.y - v1.y) != 0 else 0

        # Sort by slope
        if (mv2v1 > mv3v1) or ((mv2v1 == 0) and not(v2.x - v1.x == 0)):
            yxSorted[1], yxSorted[2] = yxSorted[2], yxSorted[1]

        coords = [(point.x, point.y) for point in yxSorted]

        return coords
