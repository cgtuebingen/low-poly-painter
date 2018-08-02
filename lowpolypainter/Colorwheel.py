from Tkinter import *
from tkColorChooser import askcolor

class Colorwheel(Frame):

    # Buttonfunctions
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


    # Menuebuttons
    def confirm(self):
        # print self.activecol
        face = self.mesh.getFaceByID(self.fn)
        face.color=self.activecol
        if self.locking.get():
            face.colorLock = True
        else:
            face.colorLock = False
        self.window.canvasFrame.canvas.itemconfig(self.fn, fill=self.activecol)
        self.window.colorWheelSafePoint1 = self.firstColor
        self.window.colorWheelSafePoint2 = self.secondColor
        self.window.colorWheelSafePoint3 = self.thirdColor
        self.cw.quit()

    def refine(self):
        self.activecol = askcolor(self.activecol)[1]
        self.redraw()

    def redraw(self):
        self.canvas.create_rectangle(0, 0, self.activeColorCanvasWidth+1, self.activeColorCanvasHeight+1, fill=self.activecol)

    def unlockAndRestore(self):
        face = self.mesh.getFaceByID(self.fn)
        face.colorLock = False
        self.LOCKBUTTON.deselect()
        self.toggleLock()
        self.activecol=face.getColorFromImage()
        face.color = self.activecol
        self.window.canvasFrame.canvas.itemconfig(self.fn, fill=self.activecol)
        self.redraw()

    # Workaround for the checkbox
    def toggleLock(self):
        if self.locking.get():
            self.locking.set(0)
        else:
            self.locking.set(1)

    # Completly overloaded. Will rework this before holidays
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
        self.CONFIRM = Button(self.menueFrame, text="Confirm", command=self.confirm)
        self.CONFIRM.pack()
        self.LOCKBUTTON = Checkbutton(self.menueFrame, text="Lock", variable=self.locking, onvalue=1, offvalue=0, command=self.toggleLock)
        self.LOCKBUTTON.pack()
        self.LOCKBUTTON.select()
        self.toggleLock()

        self.UNLOCK = Button(self.menueFrame, text="Unlock and Restore", command=self.unlockAndRestore)
        self.UNLOCK.pack()
        self.REFINE = Button(self.menueFrame, text="Edit", command=self.refine)
        self.REFINE.pack()


        self.QUIT = Button(self.menueFrame, text="Abort", command=self.cw.quit)
        self.QUIT.pack()

    def __init__(self, window, cw):
        self.window = window
        self.fn = self.window.canvasFrame.selectedFace[1]
        self.mesh = window.canvasFrame.mesh
        self.activecol = self.mesh.getFaceByID(self.fn).color
        self.firstColor = self.window.colorWheelSafePoint1
        self.secondColor = self.window.colorWheelSafePoint2
        self.thirdColor = self.window.colorWheelSafePoint3
        self.cw=cw
        self.locking = IntVar()

        self.mainFrame = Frame(self.cw)
        self.mainFrame.pack()

        self.topFrame = Frame(self.mainFrame)
        self.topFrame.pack()
        self.bottomFrame = Frame(self.mainFrame)
        self.bottomFrame.pack(side=BOTTOM)

        self.createWidgets()
