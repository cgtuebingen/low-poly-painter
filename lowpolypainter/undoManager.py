import os, errno

import window as win

maxStackSize = 100
availableAddresses = list(range(2*maxStackSize))

# manages the avaiable addresses
def getNextNumber():
    return availableAddresses.pop(0)

class UndoManager:
    """
    UndoManager Class

    Description:
    Tracks changes done on the canvas
    """
    
    def __init__(self):
        try:
            os.makedirs("lowpolypainter/resources/temp/")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        self.undoStack = MeshStack()
        self.redoStack = MeshStack()
        
    # pushes the actual state of the window on the undoStack and clears the redoStack    
    def do(self, window):
        self.undoStack.push(window)
        self.redoStack.clear()
        
    # loads the last state of the window    
    def undo(self, window):
        oldVersionNumber = self.undoStack.pop()
        if oldVersionNumber >= 0:
            self.redoStack.push(window)
            window.canvasFrame.mesh.clear()
            window.loadMeshDataPath('lowpolypainter/resources/temp/temp' + str(oldVersionNumber) + '.py')
      
    # load the previous state of the window    
    def redo(self, window):
        oldVersionNumber = self.redoStack.pop()
        if oldVersionNumber >= 0:
            self.undoStack.push(window)
            window.canvasFrame.mesh.clear()
            window.loadMeshDataPath('lowpolypainter/resources/temp/temp' + str(oldVersionNumber) + '.py')
    
    

class MeshStack:
    """
    MeshStack Class

    Description:
    Datastructure to save previous states
    """

    def __init__(self):
        self.stack = []
        
    # gets the last state and saves current state    
    def push(self, window):
        saveNumber = getNextNumber()
        self.stack.append(saveNumber)
        window.saveMeshDataPath('lowpolypainter/resources/temp/temp' + str(saveNumber) + '.py')
        if len(self.stack) > maxStackSize:
            os.remove('lowpolypainter/resources/temp/temp' + str(self.stack[0]) + '.py')
            removedAddress = self.stack.pop(0)
            availableAddresses.append(removedAddress)
       
    # pops last state from stack
    def pop(self):
        if len(self.stack) == 0:
            return -1
        else:
            topOfStack = self.stack.pop()
            global availableAddresses
            availableAddresses.append(topOfStack)
            return topOfStack
        
    # clears stack and returns unused addresses   
    def clear(self):
        global availableAddresses
        availableAddresses += self.stack
        self.stack = []
    
    
        
        