# Python modules
from operator import attrgetter

TAG_POINT = "point"
TAG_LINE = "line"
TAG_FACE = "face"
COLOR_POINT_DEFAULT = "#0000ff"
COLOR_POINT_SELECTED = "#ff0000"
COLOR_LINE_DEFAULT = "#000"
COLOR_LINE_SELECTED = "#ff0000"
COLOR_LINE_INVALID = "#ff7c19"


class CanvasPoint:
    """
    CanvasPoint

    This class handles the creation, movement, selection and updating of points and their connected lines.
    It contains the event handlers
    """
    RADIUS = 4

    def __init__(self, x, y, gui, parent):
        self.x = x
        self.y = y

        self.canvas = gui.canvas
        self.gui = gui
        self.parent = parent

        # Stores all lines that use this point
        # This way an update to the point can also update these lines
        self.connectedLines = []

        self.id = -1
        self.draw()

        self.gui.selectPoint(self)

        self.moved = False

    def click(self, event):
        # Click to select point or shift-click to connect to this point
        shiftMask = 0x0001
        self.gui.mouseEventHandled = True
        if (event.state & shiftMask) and (self.gui.selectedPoint is not None):
            self.parent.addLine(self, self.gui.selectedPoint)
            return
        self.gui.selectPoint(self)

    def draw(self):
        # Delete old
        if self.id != -1:
            self.canvas.delete(self.id)

        vertex = self.parent.gui.parent.zoom.ToViewport([self.x, self.y])

        radius = CanvasPoint.RADIUS
        self.id = self.canvas.create_oval(vertex[0] - radius,
                                          vertex[1] - radius,
                                          vertex[0] + radius,
                                          vertex[1] + radius,
                                          fill=COLOR_POINT_DEFAULT,
                                          tag=TAG_POINT)

        # Event handlers have to be rebound if the point is redrawn
        self.canvas.tag_bind(self.id, sequence="<Button>", func=self.click)
        self.canvas.tag_bind(self.id, sequence="<B1-Motion>", func=self.moveEventListener)
        self.canvas.tag_bind(self.id, sequence="<ButtonRelease-1>", func=self.finalizeMove)

    def select(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_POINT_SELECTED)
        self.canvas.tag_raise(self.id, TAG_POINT)

    def deactivate(self):
        self.canvas.itemconfigure(self.id, fill=COLOR_POINT_DEFAULT)

    def moveEventListener(self, event):
        self.move(event.x, event.y)

    def move(self, xNew, yNew):
        xOld = self.x
        yOld = self.y

        # Confine coordinates to image size
        if xNew <= 0:
            xNew = 1
        elif xNew > self.gui.frameWidth:
            xNew = self.gui.frameWidth - 1

        if yNew <= 0:
            yNew = 1
        elif yNew > self.gui.frameWidth:
            yNew = self.gui.frameWidth - 1

        # Updating the lines and therefore the faces would trigger an auto color recalculation
        # If this is fast enough, then it can be done in real time and not just after the movement ended
        for line in self.connectedLines:
            valid = line.update(recalcColor=True)

        self.moved = True
        self.canvas.move(self.id, xNew - self.x, yNew - self.y)

        self.x = xNew
        self.y = yNew

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

    def getConnectingLine(self, point):
        """
        Check if any connected line connects to point and return it.
        :param point:
        :return: line or None
        """
        for line in self.connectedLines:
            if line.isConnectedTo(point):
                return line
        return None

    def delete(self):
        self.parent.points.remove(self)
        self.canvas.delete(self.id)

        # All lines that use this point, have to be deleted
        # Copy the list, because deleting a line removes it from the connectedLines list
        deleteQueue = self.connectedLines[:]
        for line in deleteQueue:
            line.delete()


class CanvasLine:
    def __init__(self, canvasPoint1, canvasPoint2, gui, parent):
        # The two line points
        self.points = (canvasPoint1, canvasPoint2)

        # Set references to this line in points
        canvasPoint1.connectedLines.append(self)
        canvasPoint2.connectedLines.append(self)

        self.canvas = gui.canvas
        self.gui = gui
        self.parent = parent

        self.id = -1
        self.draw()

        # Stores all faces that use this line
        # This way an update to this line can also update all dependent faces
        self.faces = []

        # A new line could create a face
        self.checkFaceCreated()

        # Highlight this line if it is currently invalid by crossing other lines
        self.intersectingLines = set()
        self.checkValidLine()

        self.deleted = False

    def click(self, event):
        shiftMask = 0x0001
        self.gui.mouseEventHandled = True

        selectedPoint = self.gui.selectedPoint

        # Press shift to place points on lines
        # Automatically splits line and adds the 2 or 3 lines
        if event.state & shiftMask:
            point = self.parent.addPoint(event.x, event.y)

            # If there is a selected point, then also add a line to it
            if selectedPoint is not None:
                self.parent.addLine(point, selectedPoint)
            self.parent.addLine(point, self.points[0])
            self.parent.addLine(point, self.points[1])

            self.delete()
        else:
            self.gui.selectLine(self)

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
                    self.parent.addFace(self, line1, line2)

    def select(self):
        x0, y0, x1, y1 = self.canvas.coords(self.id)
        print(x0, y0, x1, y1)
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
        # Update position
        x1, y1, x2, y2 = self.getCoords()
        self.canvas.coords(self.id, x1, y1, x2, y2)

        isValid = self.checkValidLine()

        for face in self.faces:
            face.update(recalcColor)

        return True

    def isConnectedTo(self, point):
        return point in self.points

    def isIntersectingLine(self, x3, y3, x4, y4):
        x1, y1, x2, y2 = self.getCoords()

        a = float(x2 - x1)
        b = float(x4 - x3)
        c = float(y2 - y1)
        d = float(y4 - y3)

        s = None
        t = None

        if a == 0 and c == 0:
            # is a line of length zero
            t1 = (x1 - x3) / b
            t2 = (y1 - y3) / d
            return t1 == t2
        elif b == 0 and d == 0:
            # is a line of length zero
            s1 = (x3 - x1) / a
            s2 = (y3 - y1) / c
            return s1 == s2
        elif a == 0 and b == 0:
            return x1 == x3
        elif c == 0 and d == 0:
            return y1 == y3
        elif a == 0:
            t = (x1 - x3) / b
            s = (y3 - y1 + d * t) / c
        elif b == 0:
            s = (x3 - x1) / a
            t = (y1 - y3 + c * s) / d
        elif c == 0:
            t = (y1 - y3) / d
            s = (x3 - x1 + b * t) / a
        elif d == 0:
            s = (y3 - y1) / c
            t = (x1 - x3 + a * s) / b
        else:
            if (d - c * b / a) != 0:
                t = (y1 + c * x3 / a - c * x1 / a - y3) / (d - c * b / a)
                s = (x3 + b * t - x1) / a
            elif (b - a * d / c) != 0:
                t = (x1 + a * y3 / c - a * y1 / c - x3) / (b - a * d / c)
                s = (x3 + b * t - x1) / a
            elif (c - d * a / b) != 0:
                s = (y3 + d * x1 / b - d * x3 / b - y1) / (c - d * a / b)
                t = (x1 + a * s - x3) / b
            elif (a - b * c / d) != 0:
                s = (x3 + b * y1 / d - b * y3 / d - x1) / (a - b * c / d)
                t = (x1 + a * s - x3) / b

        #print(s, t)

        isOnLine1 = (s >= 0) and (s <= 1)
        isOnLine2 = (t >= 0) and (t <= 1)

        # if isOnLine1 and isOnLine2:
        #    self.parent.addPoint(x1 + s * a, y1 + s * c)

        return isOnLine1 and isOnLine2

    def getPossibleIntersectingLines(self, interpolationSteps = 10):
        """
        Checks rectangles along the path for overlapping lines on the canvas.
        :param interpolationSteps: Split the rectangle into multiple smaller rectangles.
        :return:
        """
        x1, y1, x2, y2 = self.getCoords()

        xStep = (x2 - x1) / float(interpolationSteps)
        yStep = (y2 - y1) / float(interpolationSteps)

        overlappingIDs = []

        for i in range(interpolationSteps):
            xRect = x1 + xStep * i
            yRect = y1 + yStep * i
            ids = self.canvas.find_overlapping(xRect, yRect, xRect + xStep, yRect + yStep)
            overlappingIDs += ids

        overlappingIDs = set(overlappingIDs)

        overlappingLines = []
        for id in overlappingIDs:
            tags = self.canvas.gettags(id)
            if TAG_LINE in tags:
                overlappingLines.append(id)

        # remove connected lines as they cant be intersected
        for point in self. points:
            for line in point.connectedLines:
                if line.id in overlappingLines:
                    overlappingLines.remove(line.id)

        return overlappingLines

    def checkValidLine(self):
        possibleIDs = self.getPossibleIntersectingLines()

        currentIntersectingLines = []

        # Check, which lines actually intersect
        isValid = True
        for id in possibleIDs:
            x3, y3, x4, y4 = self.canvas.coords(id)
            if self.isIntersectingLine(x3, y3, x4, y4):
                oldLine = self.parent.getLineByID(id)
                currentIntersectingLines.append(oldLine)
                isValid = False

        # Check if some lines stopped intersecting and if yes, notify the other line
        # Remove all lines we already know about from the list
        oldIntersectingLines = self.intersectingLines.copy()
        for oldLine in oldIntersectingLines:
            if not oldLine in currentIntersectingLines:
                self.removeIntersectionWithLine(oldLine)
                oldLine.removeIntersectionWithLine(self)
            else:
                currentIntersectingLines.remove(oldLine)

        # Add all lines that are new to the list of intersecting lines
        for line in currentIntersectingLines:
            self.addIntersectionWithLine(line)
            line.addIntersectionWithLine(self)

        return isValid

    def setValid(self, isValid):
        if isValid:
            self.canvas.itemconfigure(self.id, fill=COLOR_LINE_DEFAULT)
        else:
            # Invalid lines should be on top
            self.canvas.tag_raise(self.id, TAG_LINE)
            self.canvas.itemconfigure(self.id, fill=COLOR_LINE_INVALID)

    def addIntersectionWithLine(self, line):
        self.intersectingLines.add(line)
        if len(self.intersectingLines) == 1:
            self.setValid(False)

    def removeIntersectionWithLine(self, line):
        self.intersectingLines.remove(line)
        if len(self.intersectingLines) == 0:
            self.setValid(True)

    def getCoords(self):
        x1 = self.points[0].x
        x2 = self.points[1].x
        y1 = self.points[0].y
        y2 = self.points[1].y
        return x1, y1, x2, y2

    def delete(self):
        if not self.deleted:
            self.parent.lines.remove(self)
            self.canvas.delete(self.id)

            deleteQueue = self.faces[:]
            for face in deleteQueue:
                face.delete()
            for point in self.points:
                point.connectedLines.remove(self)

        self.deleted = True


class CanvasFace:
    def __init__(self, line1, line2, line3, gui, parent):
        # Lines
        self.lines = (line1, line2, line3)

        self.canvas = gui.canvas
        self.gui = gui
        self.parent = parent

        self.color = "#000000"
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
                                             state=self.gui.currentFaceState)

        # Faces should be below lines and points
        self.canvas.tag_lower(self.id, TAG_LINE)

    def getAutoColor(self):
        """
        Calculates color based on the pixels of the image below this face
        :return:
        """
        coords = self.getCoordinates()
        self.color = self.gui.getColorFromImage(coords)

    def update(self, recalcColor):
        if recalcColor:
            self.getAutoColor()
        self.draw()

    def delete(self):
        if not self.deleted:
            self.parent.faces.remove(self)
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
        if (mv2v1 > mv3v1) or ((mv2v1 == 0) and not (v2.x - v1.x == 0)):
            yxSorted[1], yxSorted[2] = yxSorted[2], yxSorted[1]

        coords = [(point.x, point.y) for point in yxSorted]

        return coords
