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

        color = '#ECECEC'
        color_opts = {'bg': color}
        entry_opts = {'width':0,
                         'justify':'right',
                         'highlightbackground':color}
        button_opts = {'highlightthickness':0,
                          'highlightbackground':'#ECECEC'}

        self.left_keeper = Frame(self, width=10, **color_opts)
        self.left_keeper.grid(row=0, column=0, sticky=NSEW)

        self.right_keeper = Frame(self, width=10, **color_opts)
        self.right_keeper.grid(row=0, column=3, sticky=NSEW)

        self.width_keeper_1 = Frame(self, width=110, **color_opts)
        self.width_keeper_1.grid(row=0, column=1, sticky=NSEW)

        self.width_keeper_2 = Frame(self,  width=82, **color_opts)
        self.width_keeper_2.grid(row=0, column=2, sticky=NSEW)

        self.cannyLabel = Label(self, text='Canny Points', **color_opts)
        self.cannyLabel.grid(row=1, column=1, sticky=N+W+S)

        self.cannyEntry = Entry(self, **entry_opts)
        self.cannyEntry.grid(row=1, column=2, sticky=NSEW)
        self.cannyEntry.insert(0,'0')

        self.randomLabel = Label(self, text='Random Points', **color_opts)
        self.randomLabel.grid(row=2, column=1, sticky=N+W+S)

        self.randomEntry = Entry(self, **entry_opts)
        self.randomEntry.grid(row=2, column=2, sticky=NSEW)
        self.randomEntry.insert(0,'0')

        self.height_keeper = Frame(self, **color_opts)
        self.height_keeper.grid(row=3, column=1, sticky=NSEW)

        mask_opts = {'text':'Mask', 'command':self.mask}
        mask_opts.update(button_opts)

        self.maskButton = Button(self, **mask_opts)
        self.maskButton.grid(row=4, column=1, columnspan=2, sticky=N+E+S+W)

        self.spacer = Frame(self, height=10, **color_opts)
        self.spacer.grid(row=5, column=1, sticky=NSEW)

        border_opts = {'text':'Border', 'command':self.border}
        border_opts.update(button_opts)

        self.borderButton = Button(self, **border_opts)
        self.borderButton.grid(row=6, column=1, columnspan=2, sticky=N+E+S+W)

        self.spacer2 = Frame(self, height=10, **color_opts)
        self.spacer2.grid(row=7, column=1, sticky=NSEW)

        triangulate_opts = {'text':'Triangulate', 'command':self.triangulate}
        triangulate_opts.update(button_opts)

        self.triangulateButton = Button(self, **triangulate_opts)
        self.triangulateButton.grid(row=8, column=1, columnspan=2, sticky=NSEW)

        self.bottom_keeper = Frame(self, height=10, **color_opts)
        self.bottom_keeper.grid(row=9, column=1, sticky=NSEW)

    def mask(self):
        self.parent.parent.toogleCanvasFrame()

    def border(self):
        self.parent.parent.generateBorder()

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
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Create Canvas
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.canvas.create_image(0, 0, image=self.background, anchor=NW)
        self.canvas.bind("<B1-Motion>", func=self.click)
        self.canvas.grid(row=1, column=1, sticky=NSEW)

        # Radius
        self.radius = 2

        # Mask
        self.mask = np.zeros([self.width, self.height], dtype=bool)

    def click(self, event):
        point = [event.x, event.y]
        if self.inBounds(point):
            self.addPointToMask(point)
            self.canvas.create_oval(point[0] - self.radius,
                                    point[1] - self.radius,
                                    point[0] + self.radius,
                                    point[1] + self.radius,
                                    outline = "", fill = 'green', tag = 'v')

    def addPointToMask(self, point):
        # TODO: Currently rectenagle but is circle
        for y in range(point[1] - self.radius, point[1] + self.radius + 1):
            for x in range(point[0] - self.radius, point[0] + self.radius + 1):
                if self.inBounds([x,y]):
                    self.mask[x][y] = 1


    def inBounds(self, point):
        x, y = point[0], point[1]
        return (x >= 0) and (y >= 0) and (x < self.width) and (y < self.height)
    
    def insert(self, path, name):
        # Load Image
        self.inputimage = name
        if isinstance(path, basestring):
            self.image = Image.open(path)
        else:
            self.image = path
        self.background = ImageTk.PhotoImage(self.image)

        # Center Canvas
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Create Canvas
        self.width = self.background.width()
        self.height = self.background.height()
        self.canvas.configure(width=self.width, height=self.height)
        self.canvas.create_image(0, 0, image=self.background, anchor=NW)
        self.mask = np.zeros([self.width, self.height], dtype=bool)
        
