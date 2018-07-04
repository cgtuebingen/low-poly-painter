# Python Modules
import svgwrite
from Tkinter import *
import tkFileDialog


def exportDialog(mesh, width, height):
    filename = tkFileDialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("svg files","*.svg"),("all files","*.*")))
    exportFromCanvasObjectsMesh(filename, mesh, width, height)
    
    
def exportFrame(frame, mesh, width, height):
    # creates a new frame
    exportFrame = Toplevel(frame)
    exportFrame.resizable(width=False, height=False)
    
    
    entryWidth = 25
                       
    # creates a textfield to enter filename               
    entry = Entry(exportFrame, width=entryWidth)
    entry.focus_set()
    entry.pack() 
    
    # acceptButton-callback
    def accept(event=None):
        exportFromCanvasObjectsMesh(entry.get(), mesh, width, height)
        exportFrame.destroy()
        
        
    # binds the Enter key to saveButton    
    exportFrame.bind('<Return>',accept)
    
    # accept button 
    acceptButton = Button(exportFrame, text="accept", command=accept)
    acceptButton.pack()
    
    # sets the position of the toplevel
    exportFrame.update()
    exportFrame_x = frame.winfo_rootx() + (frame.winfo_width()/2) - (exportFrame.winfo_width() / 2)
    exportFrame_y = frame.winfo_rooty() + (frame.winfo_height()/2) 
    exportFrame.geometry("+%d+%d" % (exportFrame_x,exportFrame_y))
    
        
    
    
    
def exportFromCanvasObjectsMesh(filename, mesh, width, height):
    img = svgwrite.Drawing(filename + '.svg', size=(str(width), str(height)))
    for face in mesh.faces:
        # vertices for triangle
        points = face.getCoordinates()
        # color of the face, converted to decimal rgb values
        color = svgwrite.rgb(r=int(face.color[1:3], 16),
                             g=int(face.color[3:5], 16),
                             b=int(face.color[5:7], 16),
                             mode='RGB')
        # add triangle to image
        # HACK: Twice to get less gaps in the final svg
        img.add(img.polygon(points=points, fill=color))
        img.add(img.polygon(points=points, fill=color))
    # save image
    img.save()
    

