from Tkinter import *
from tkColorChooser import askcolor

from canvas.mesh import Mesh

# TODO: First add Face selection, then give the Colorwheels some Colors of the Face
# TODO: Add return Function to return the new Color.
class Colorwheel(Frame):

    def firstColorUse(self):
        self.activecol = self.firstColor
        self.redraw()

    def secondColorUse(self):
        self.activecol = self.secondColor
        self.redraw()

    def thirdColorUse(self):
        self.activecol = self.thirdColor
        self.redraw()

    def firstColorSafe(self):
        self.firstColor = self.activecol
        self.firstColorButtonSafe.configure(bg=self.firstColor)
        self.firstColorButtonUse.configure(bg=self.firstColor)

    def secondColorSafe(self):
        self.secondColor = self.activecol
        self.secondColorButtonSafe.configure(bg=self.secondColor)
        self.secondColorButtonUse.configure(bg=self.secondColor)

    def thirdColorSafe(self):
        self.thirdColor = self.activecol
        self.thirdColorButtonSafe.configure(bg=self.thirdColor)
        self.thirdColorButtonUse.configure(bg=self.thirdColor)



    def confirm(self):
        # print self.activecol
        self.mesh.getFaceByID(self.fn).color=self.activecol
        self.mesh.getFaceByID(self.fn).draw()
        self.window.colorWheelSafePoint1 = self.firstColor
        self.window.colorWheelSafePoint2 = self.secondColor
        self.window.colorWheelSafePoint3 = self.thirdColor
        self.cw.quit()
    def refine(self):
        self.activecol = askcolor(self.activecol)[1]
        self.redraw()

    def redraw(self):
        self.canvas.create_rectangle(0, 0, self.activeColorCanvasWidth+1, self.activeColorCanvasHeight+1, fill=self.activecol)


    def createWidgets(self):

        self.activeColorCanvasWidth = 50
        self.activeColorCanvasHeight = 50
        self.canvas = Canvas(self.topFrame, width=self.activeColorCanvasWidth, height=self.activeColorCanvasHeight)
        self.redraw()
        self.canvas.pack()


        self.firstColorFrame = Frame(self.bottomFrame)
        self.firstColorFrame.pack(side=LEFT)
        self.firstColorButtonSafe = Button(self.firstColorFrame, text="Safe", fg="white", bg=self.firstColor, width=8, height=2, command=self.firstColorSafe)
        self.firstColorButtonSafe.pack()
        self.firstColorButtonUse = Button(self.firstColorFrame, text="Use", fg="white", bg=self.firstColor, width=8, height=2, command=self.firstColorUse)
        self.firstColorButtonUse.pack()


        self.secondColorFrame = Frame(self.bottomFrame)
        self.secondColorFrame.pack(side=LEFT)
        self.secondColorButtonSafe = Button(self.secondColorFrame, text="Safe", fg="white", bg=self.secondColor, width=8, height=2, command=self.secondColorSafe)
        self.secondColorButtonSafe.pack()
        self.secondColorButtonUse = Button(self.secondColorFrame, text="Use", fg="white", bg=self.secondColor, width=8, height=2, command=self.secondColorUse)
        self.secondColorButtonUse.pack()


        self.thirdColorFrame = Frame(self.bottomFrame)
        self.thirdColorFrame.pack(side=LEFT)
        self.thirdColorButtonSafe = Button(self.thirdColorFrame, text="Safe", fg="white", bg=self.thirdColor, width=8, height=2, command=self.thirdColorSafe)
        self.thirdColorButtonSafe.pack()
        self.thirdColorButtonUse = Button(self.thirdColorFrame, text="Use", fg="white", bg=self.thirdColor, width=8, height=2, command=self.thirdColorUse)
        self.thirdColorButtonUse.pack()


        self.menueFrame = Frame(self.bottomFrame)
        self.menueFrame.pack(side=LEFT)
        self.CONFIRM = Button(self.menueFrame, text="Bestaetigen", command=self.confirm)
        self.CONFIRM.pack()
        self.REFINE = Button(self.menueFrame, text="Anpassen", command=self.refine)
        self.REFINE.pack()
        self.QUIT = Button(self.menueFrame, text="Abbrechen", command=self.cw.quit)
        self.QUIT.pack()

    def __init__(self, window, facenumber, c1,c2,c3, cw):
        self.fn = facenumber
        self.window = window
        self.mesh = window.canvasFrame.mesh
        self.activecol = self.mesh.getFaceByID(self.fn).color
        self.firstColor = c1
        self.secondColor = c2
        self.thirdColor = c3
        self.cw=cw

        self.mainFrame = Frame(self.cw)
        self.mainFrame.pack()

        self.topFrame = Frame(self.mainFrame)
        self.topFrame.pack()
        self.bottomFrame = Frame(self.mainFrame)
        self.bottomFrame.pack(side=BOTTOM)

        self.createWidgets()
