# Python Modules
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image


class TriangulateFrame(Frame):
    """
    Triangulate Frame Class

    Description:
    Contains details about triangulate tool
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.config(bg='#ECECEC', width=199)
        self.parent = parent

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.left_keeper = Frame(self, bg='#ECECEC', width=10)
        self.left_keeper.grid(row=0, column=0, sticky=N+E+S+W)

        self.right_keeper = Frame(self, bg='#ECECEC', width=10)
        self.right_keeper.grid(row=0, column=3, sticky=N+E+S+W)

        self.width_keeper_1 = Frame(self, bg='#ECECEC', width=110)
        self.width_keeper_1.grid(row=0, column=1, sticky=N+E+S+W)

        self.width_keeper_2 = Frame(self,bg='#ECECEC',  width=82)
        self.width_keeper_2.grid(row=0, column=2, sticky=N+E+S+W)

        self.cannyLabel = Label(self, bg='#ECECEC', text='Canny Points')
        self.cannyLabel.grid(row=1, column=1, sticky=N+W+S)

        self.cannyEntry = Entry(self, width=0, highlightbackground='#ECECEC',justify='right')
        self.cannyEntry.grid(row=1, column=2, sticky=N+E+S+W)
        self.cannyEntry.insert(0,'0')

        self.randomLabel = Label(self, bg='#ECECEC', text='Random Points')
        self.randomLabel.grid(row=2, column=1, sticky=N+W+S)

        self.randomEntry = Entry(self, width=0,highlightbackground='#ECECEC', justify='right')
        self.randomEntry.grid(row=2, column=2, sticky=N+E+S+W)
        self.randomEntry.insert(0,'0')

        self.height_keeper = Frame(self, bg='#ECECEC')
        self.height_keeper.grid(row=3, column=1, sticky=N+E+S+W)

        self.maskButton = Button(self, highlightthickness=0, highlightbackground='#ECECEC', text='Mask', command=self.mask)
        self.maskButton.grid(row=4, column=1, columnspan=2, sticky=N+E+S+W)

        self.spacer = Frame(self, bg='#ECECEC', height=10)
        self.spacer.grid(row=5, column=1, sticky=N+E+S+W)

        self.triangulateButton = Button(self, highlightthickness=0, highlightbackground='#ECECEC', text='Triangulate', command=self.triangulate)
        self.triangulateButton.grid(row=6, column=1, columnspan=2, sticky=N+E+S+W)

        self.bottom_keeper = Frame(self, bg='#ECECEC', height=10)
        self.bottom_keeper.grid(row=7, column=1, sticky=N+E+S+W)

    def mask(self):
        self.parent.parent.toogleCanvasFrame()

    def triangulate(self):
        try:
            cannyValue = int(self.cannyEntry.get())
            randomValue = int(self.randomEntry.get())
            self.parent.parent.triangulate(size=cannyValue, random=randomValue)
        except ValueError:
            self.cannyEntry.delete(0,END)
            self.randomEntry.delete(0,END)

class MaskFrame(Frame):
    """
    Mask Frame Class

    Description:
    Mask image for specific triangulation
    """
    def __init__(self, parent, inputimage, *args, **kwargs):
        Frame.__init__(self, parent.frame)

        # Parent
        self.parent = parent

        # Load Image
        self.inputimage = inputimage
        filepath = 'lowpolypainter/resources/images/' + inputimage
        self.image = Image.open(filepath)
        self.background = ImageTk.PhotoImage(self.image)

        # Center Canvas
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(2, weight=1)

        # Create Canvas
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.canvas.create_image(0, 0, image=self.background, anchor=NW)
        self.canvas.bind("<B1-Motion>", func=self.click)
        self.canvas.grid(row=1, column=1, sticky=NSEW)

        # Mask
        self.mask = np.zeros([self.width, self.height], dtype=bool)

        # Radius
        self.r = 2

    def click(self, event):
        point = [event.x, event.y]
        if self.inBounds(point):
            self.addPointToMask(point)
            self.canvas.create_oval(point[0] - self.r, point[1] - self.r,
                                    point[0] + self.r, point[1] + self.r,
                                    outline = "", fill = 'green', tag = 'v')

    def addPointToMask(self, point):
        # TODO: Currently rectenagle but is circle
        for y in range(point[1] - self.r, point[1] + self.r + 1):
            for x in range(point[0] - self.r, point[0] + self.r + 1):
                if self.inBounds([x,y]):
                    self.mask[y][x] = 1


    def inBounds(self, point):
        x, y = point[0], point[1]
        return (x >= 0) and (y >= 0) and (x < self.width) and (y < self.height)
