# Python Modules
import math
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
        self.config(bg='#ffffff', width=199)
        self.parent = parent

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=3, uniform="triangulateFrame")
        self.grid_rowconfigure(1, weight=1, uniform="triangulateFrame")
        self.grid_rowconfigure(2, weight=1, uniform="triangulateFrame")
        self.grid_rowconfigure(3, weight=1, uniform="triangulateFrame")
        self.grid_rowconfigure(4, weight=2, uniform="triangulateFrame")
        self.grid_rowconfigure(5, weight=3, uniform="triangulateFrame")

        font1 = "-family {Heiti TC} -size 12 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        color_opts1 = {'bg': '#ffffff'}
        entry_opts = {'width':8,
                         'justify':'right',
                         'highlightbackground':'#ffffff',
                         'font':'font1'}
        button_opts = {'highlightthickness':1,
                          'highlightbackground':'#ffffff', 'borderwidth': 0,
                          'highlightcolor':'#ffffff',
                          'height': 30, 'width': 32}

        self.left_keeper = Frame(self, width=10, **color_opts1)
        self.left_keeper.grid(row=0, column=0, sticky=NSEW)

        self.right_keeper = Frame(self, width=10, **color_opts1)
        self.right_keeper.grid(row=0, column=3, sticky=NSEW)

        self.width_keeper_1 = Frame(self, width=10, **color_opts1)
        self.width_keeper_1.grid(row=0, column=1, sticky=NSEW)

        self.width_keeper_2 = Frame(self,  width=82, **color_opts1)
        self.width_keeper_2.grid(row=0, column=2, sticky=NSEW)

        self.entryLabel = Label(self, text='Insert number', justify='right', font=font1, **color_opts1)
        self.entryLabel.grid(row=1, column=0, sticky=N+S+E, padx=4)

        self.entry = Entry(self, **entry_opts)
        self.entry.grid(row=1, column=1, sticky=N+S+W+E)
        self.entry.bind('<FocusIn>', self.toogleEntryFocus)
        self.entry.bind('<FocusOut>', self.toogleEntryFocus)
        self.entry.insert(0,'0')

        self.height_keeper = Frame(self, **color_opts1)
        self.height_keeper.grid(row=3, column=1, sticky=NSEW)

        self.buttonFrame = Frame(self, **color_opts1)
        self.buttonFrame.grid(row=4, column=0, columnspan=3)
        self.buttonFrame.grid_columnconfigure(0, weight=0, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(1, weight=0, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(2, weight=0, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(3, weight=0, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(4, weight=0, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(5, weight=0, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(6, weight=0, uniform="buttonframe")

        path = "lowpolypainter/resources/icons/"

        # mask button
        self.maskImage = ImageTk.PhotoImage(file=path+"mask.png")
        mask_opts = {'image':self.maskImage, 'command':self.mask}
        mask_opts.update(button_opts)

        self.maskButton = Button(self.buttonFrame, **mask_opts)
        self.maskButton.grid(row=0, column=1, sticky=N+E+S+W, padx=5)

        # border points button
        self.borderImage = ImageTk.PhotoImage(file=path+"borderpoints.png")
        border_opts = {'image':self.borderImage, 'command':self.border}
        border_opts.update(button_opts)

        self.borderButton = Button(self.buttonFrame, **border_opts)
        self.borderButton.grid(row=0, column=2, sticky=N+E+S+W, padx=5)

        # triangulate button
        self.triangleImage = ImageTk.PhotoImage(file=path+"triangulate.png")
        triangulate_opts = {'image': self.triangleImage, 'command':self.triangulate}
        triangulate_opts.update(button_opts)

        self.triangulateButton = Button(self.buttonFrame, **triangulate_opts)
        self.triangulateButton.grid(row=0, column=3, sticky=NSEW, padx=5)

        # border button to fill outer areas without mesh
        self.BordersImage = ImageTk.PhotoImage(file=path+"fill.png")
        borders_opts = {'image': self.BordersImage, 'command': self.parent.parent.borderTriangulate}
        borders_opts.update(button_opts)

        self.BordersButton = Button(self.buttonFrame, **borders_opts)
        self.BordersButton.grid(row=0, column=4, sticky=NSEW, padx=5)

        # random button
        self.randomImage = ImageTk.PhotoImage(file=path+"random.png")
        random_opts = {'image':self.randomImage, 'command':self.random}
        random_opts.update(button_opts)

        self.randomButton = Button(self.buttonFrame, **random_opts)
        self.randomButton.grid(row=0, column=5, sticky=N+E+S+W, padx=5)

    def mask(self):
        self.parent.parent.toggleCanvasFrame()

    def border(self):
        value = self.getEntryValue()
        if value != None:
            self.parent.parent.border(step=value)

    def random(self):
        value = self.getEntryValue()
        if value != None:
            self.parent.parent.random(size=value)

    def triangulate(self):
        value = self.getEntryValue()
        if value != None:
            self.parent.parent.triangulate(size=value)

    def getEntryValue(self):
        try:
            value = int(self.entry.get())
            return value
        except ValueError:
            self.entry.delete(0,END)
            return None
    def toogleEntryFocus(self, event):
        self.parent.parent.toggleEntryFocus()


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
        for y in range(point[1] - self.radius - 1, point[1] + self.radius + 1):
            for x in range(point[0] - self.radius, point[0] + self.radius + 1):
                dist = math.sqrt((point[0] - x)**2 + (point[1] - y)**2)
                if self.inBounds([x,y]) and dist <= self.radius:
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
