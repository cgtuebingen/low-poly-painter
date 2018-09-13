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
        self.config(bg='#DADADA', width=199)
        self.parent = parent

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=3, uniform="triangulateFrame")
        self.grid_rowconfigure(1, weight=1, uniform="triangulateFrame")
        self.grid_rowconfigure(2, weight=1, uniform="triangulateFrame")
        self.grid_rowconfigure(3, weight=1, uniform="triangulateFrame")
        self.grid_rowconfigure(4, weight=2, uniform="triangulateFrame")
        self.grid_rowconfigure(5, weight=3, uniform="triangulateFrame")

        color1 = '#ECECEC'
        color2 = '#DADADA'
        color_opts1 = {'bg': color1}
        color_opts2 = {'bg': color2}
        entry_opts = {'width':0,
                         'justify':'right',
                         'highlightbackground':color2}
        button_opts = {'highlightthickness':0,
                          'highlightbackground':color2}

        self.left_keeper = Frame(self, width=10, **color_opts1)
        self.left_keeper.grid(row=0, column=0, sticky=NSEW)

        self.right_keeper = Frame(self, width=10, **color_opts1)
        self.right_keeper.grid(row=0, column=3, sticky=NSEW)

        self.width_keeper_1 = Frame(self, width=110, **color_opts1)
        self.width_keeper_1.grid(row=0, column=1, sticky=NSEW)

        self.width_keeper_2 = Frame(self,  width=82, **color_opts1)
        self.width_keeper_2.grid(row=0, column=2, sticky=NSEW)

        self.cannyLabel = Label(self, text='Canny Points', **color_opts2)
        self.cannyLabel.grid(row=1, column=1, sticky=N+W+S)

        self.cannyEntry = Entry(self, **entry_opts)
        self.cannyEntry.grid(row=1, column=2, sticky=NSEW)
        self.cannyEntry.insert(0,'0')

        self.randomLabel = Label(self, text='Random Points', **color_opts2)
        self.randomLabel.grid(row=2, column=1, sticky=N+W+S)

        self.randomEntry = Entry(self, **entry_opts)
        self.randomEntry.grid(row=2, column=2, sticky=NSEW)
        self.randomEntry.insert(0,'0')

        self.height_keeper = Frame(self, **color_opts2)
        self.height_keeper.grid(row=3, column=1, sticky=NSEW)
        
        self.buttonFrame = Frame(self, **color_opts2)
        self.buttonFrame.grid(row=4, column=0, columnspan=3)
        self.buttonFrame.grid_columnconfigure(0, weight=2, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(1, weight=1, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(2, weight=2, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(3, weight=1, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(4, weight=2, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(5, weight=1, uniform="buttonframe")
        self.buttonFrame.grid_columnconfigure(6, weight=2, uniform="buttonframe")

        image = Image.open("lowpolypainter/resources/images/mask.png")
        self.maskImage = ImageTk.PhotoImage(image)
        mask_opts = {'image':self.maskImage, 'command':self.mask}
        mask_opts.update(button_opts)

        self.maskButton = Button(self.buttonFrame, **mask_opts)
        self.maskButton.grid(row=0, column=0, sticky=N+E+S+W)

        self.spacer = Frame(self.buttonFrame, width=1, **color_opts2)
        self.spacer.grid(row=0, column=1, sticky=NSEW)
        
        
        image = Image.open("lowpolypainter/resources/images/BorderPoints.png")
        self.borderImage = ImageTk.PhotoImage(image)
        border_opts = {'image':self.borderImage, 'command':self.border}
        border_opts.update(button_opts)

        self.borderButton = Button(self.buttonFrame, **border_opts)
        self.borderButton.grid(row=0, column=2, sticky=N+E+S+W)

        self.spacer2 = Frame(self.buttonFrame, width=1, **color_opts2)
        self.spacer2.grid(row=0, column=3, sticky=NSEW)
        
        image = Image.open("lowpolypainter/resources/images/triangulate.png")
        self.triangleImage = ImageTk.PhotoImage(image)
        triangulate_opts = {'image': self.triangleImage, 'command':self.triangulate}
        triangulate_opts.update(button_opts)

        self.triangulateButton = Button(self.buttonFrame, **triangulate_opts)
        self.triangulateButton.grid(row=0, column=4, sticky=NSEW)
        
        self.spacer3 = Frame(self.buttonFrame, width=1, **color_opts2)
        self.spacer3.grid(row=0, column=5, sticky=NSEW)
        
        image = Image.open("lowpolypainter/resources/icons/Borders.gif")
        self.BordersImage = ImageTk.PhotoImage(image)
        borders_opts = {'image': self.BordersImage, 'command': self.parent.parent.generateBorderAndTriangulate}
        borders_opts.update(button_opts)

        self.BordersButton = Button(self.buttonFrame, **borders_opts)
        self.BordersButton.grid(row=0, column=6, sticky=NSEW)

        self.bottom_keeper = Frame(self, width=1, **color_opts1)
        self.bottom_keeper.grid(row=5, column=0, columnspan=5, sticky=NSEW)

    def mask(self):
        self.parent.parent.toggleCanvasFrame()

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
        
