from Tkinter import *

from tkColorChooser import askcolor

# TODO: First add Face selection, then give the Colorwheels some Colors of the Face
# TODO: Add return Function to return the new Color.
class Colorwheel(Frame):
    # TODO: use given Colors
    activecol = "yellow"
    lowestcol = "white"
    mediancol = "white"
    highestcol = "white"
    activeColorCanvasWidth=50
    activeColorCanvasHeight=50

    def lowestcolor(self):
        self.activecol = self.lowestcol
        self.redraw()

    def mediancolor(self):
        self.activecol = self.mediancol
        self.redraw()

    def highestcolor(self):
        self.activecol = self.highestcol
        self.redraw()

    def confirm(self):
        print self.activecol
        self.quit()
    def refine(self):
        self.activecol=askcolor(self.activecol)[1]
        self.redraw()

    def redraw(self):
        self.canvas.create_rectangle(0, 0, self.activeColorCanvasWidth+1, self.activeColorCanvasHeight+1, fill=self.activecol)

    # TODO: Rearange Buttons if wanted
    def createWidgets(self):
        self.canvas = Canvas(self, width=self.activeColorCanvasWidth, height=self.activeColorCanvasHeight)
        self.redraw()
        self.canvas.pack(side=TOP)

        self.LOWESTCOLOR = Button(self, text="", bg=self.lowestcol, width=8, height=4, command=self.lowestcolor,)
        self.LOWESTCOLOR.pack(side=LEFT)

        self.MEDIANCOLOR = Button(self, text="", bg=self.mediancol, width=8, height=4, command=self.mediancolor, )
        self.MEDIANCOLOR.pack(side=LEFT)

        self.HIGHESTCOLOR = Button(self, text="", bg=self.highestcol, width=8, height=4, command=self.highestcolor, )
        self.HIGHESTCOLOR.pack(side=LEFT)

        self.QUIT = Button(self, text="Abbrechen", command=self.quit,)
        self.QUIT.pack(side=BOTTOM)
        self.REFINE = Button(self, text="Anpassen", command=self.refine)
        self.REFINE.pack(side=BOTTOM)
        self.CONFIRM = Button(self, text="Bestaetigen", command=self.confirm)
        self.CONFIRM.pack(side=BOTTOM)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
