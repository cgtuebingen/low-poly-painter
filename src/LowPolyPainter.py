#!/usr/bin/env python2
import sys
import numpy as np
import Tkinter as tk

"""
This class is responsible for the created window and contains the functions to draw the triangles (tris)
Widgets, like buttons and text, will be added here
"""
class LowPolyPainterWindow(tk.Frame):
	# List of points and tris
	points = []
	tris = []
	clickedPointsI = []
	
	def __init__(self, imagePath, master=None):
		
		tk.Frame.__init__(self, master)
		self.grid()
		self.createWidgets(imagePath)
	
	# Buttons/Canvas/... are created here
	def createWidgets(self, imagePath):
		# Place a canvas in the window and set the supplied image to the background
		self.canvasBackground = tk.PhotoImage(file=imagePath)
		self.canvas = tk.Canvas(self, width=self.canvasBackground.width(), height=self.canvasBackground.height())
		self.canvas.bind("<Button-1>",self.__canvasClick)
		self.canvas.grid()
		
		self.canvas.create_image(0,0, image=self.canvasBackground, anchor=tk.NW)
		
		self.testButton = tk.Button(self, text='Random Tris', command=self.test)
		self.testButton.grid()
		
		self.clearButton = tk.Button(self, text='Clear', command=self.clear)
		self.clearButton.grid()

	# Adds all points (tuple x,y) to the list and returns their indices
	def addPoints(self,points):
		indices = []
		for point in points:
			indices.append(len(self.points))
			self.points.append(point)
		return indices

	# Draws all Tris
	def drawTris(self):
		self.canvas.delete("tri")
		for tri in self.tris:
			v1 = self.points[tri.verts[0]]
			v2 = self.points[tri.verts[1]]
			v3 = self.points[tri.verts[2]]
			self.canvas.create_polygon(v1[0],v1[1],v2[0],v2[1],v3[0],v3[1],fill=tri.color,tag="tri")

	# Canvas click event
	# Adds points for each click and after 3 points creates a tri
	def __canvasClick(self, event):
		# Get index of added point and store it
		i = self.addPoints([(event.x,event.y)])[0]
		self.clickedPointsI.append(i)
		
		# 3 points => Tri
		if len(self.clickedPointsI) == 3:
			tri = Tri(self.clickedPointsI[0],self.clickedPointsI[1],self.clickedPointsI[2],getRandomColorString())
			self.tris.append(tri)
			self.clickedPointsI[:] = []
			self.drawTris()
	
	# Add NUM_POINTS random new points and creates NUM_TRIS random tris
	def test(self):
		NUM_POINTS = 10
		NUM_TRIS = 5
		# Max values so that tris don't go out of bounds
		xMax = self.canvas.cget("width")
		yMax = self.canvas.cget("height")

		# Random points
		for i in range(NUM_POINTS):
			self.addPoints([(np.random.randint(xMax),np.random.randint(yMax))])
		
		# Random tris where the 3 indices are unique random
		# The color is also random
		maxPointIndex = len(self.points)
		for i in range(NUM_TRIS):
			i1 = np.random.randint(maxPointIndex)
			i2 = np.random.randint(maxPointIndex)
			i3 = np.random.randint(maxPointIndex)
			while i1 == i2 or i2 == i3 or i1 == i3:
				i2 = np.random.randint(maxPointIndex)
				i3 = np.random.randint(maxPointIndex)
			self.tris.append(Tri(i1,i2,i3,getRandomColorString()))
		
		# Call the draw function
		self.drawTris()
	
	# Clear tri and point list and remove all tris from canvas
	def clear(self):
		self.tris[:] = []
		self.points[:] = []
		self.canvas.delete("tri")

"""
This class stores the indices of the 3 corner points (vertex) as well as the color
"""
class Tri(object):
	def __init__(self, vert1, vert2, vert3, color):
		self.verts = [vert1, vert2, vert3]
		self.color = color

"""
Generates a random color string #rrggbb
"""
def getRandomColorString():
	# Generates random numbers between 0 and 255 and stores them as zero padded hex numbers
	r = "%02x"%np.random.randint(255)
	g = "%02x"%np.random.randint(255)
	b = "%02x"%np.random.randint(255)
	return "#" + r + g + b

"""
Main function called after starting the script.
Should create the Application window and do any preprocessing
"""
def main(imagePath):
	app = LowPolyPainterWindow(imagePath)
	app.master.title('LowPolyPainter')
	app.mainloop()

def printHelp():
	print('Usage: DisplayWindow.py path/to/image.ppm')

"""
If it is called as a script, then get image path and call main
"""
if __name__ == "__main__":
	# execute only if run as a script
	if len(sys.argv) == 2:
		main(str(sys.argv[1]))
	else:
		printHelp()
		exit()