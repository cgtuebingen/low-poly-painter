import os.path
import cPickle as pickle
import time


# saves mesh data in a .py file by using cPickle
def save(mesh, inputimage): 
    directory = './lowpolypainter/resources/stored_mesh_data'
    path = directory + '/' + inputimage + '.py'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file = open(path, 'w')
    pickle.dump(mesh, file)
    file.close()
    
# saves mesh data in a .py file by using cPickle
def savePath(mesh, path):
    file = open(path, 'w')
    pickle.dump(mesh, file)
    file.close()

# loads mesh data from inputimage related .py file by using cPickle
def load(inputimage):
    path = 'lowpolypainter/resources/stored_mesh_data/' + inputimage + '.py'
    if os.path.isfile(path):
        file = open(path, 'r')
        mesh = pickle.load(file)
        file.close()
        return mesh

# loads mesh data from inputimage related .py file by using cPickle
def loadPath(path):
    if os.path.isfile(path):
        file = open(path, 'r')
        mesh = pickle.load(file)
        file.close()
        return mesh
