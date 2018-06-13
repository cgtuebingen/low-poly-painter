from vector3 import Vector3

class Matrix3x3(object):

    def __init__(self, row0, row1, row2):
        if isinstance(row0, Vector3) and isinstance(row1, Vector3) and isinstance(row2, Vector3):
            self.r0 = row0
            self.r1 = row1
            self.r2 = row2
        else:
            raise TypeError("__init__: Vector3")

    @staticmethod
    def Translation(x, y):
        if isinstance(x, int):
            x = float(x)
        if isinstance(y, int):
            y = float(y)
        if isinstance(x, float) and isinstance(y, float):
            return Matrix3x3(Vector3(1,0,x), Vector3(0,1,y), Vector3(0,0,1))
        raise TypeError("Translation: int or float")
        
    @staticmethod
    def Scale(x, y):
        if isinstance(x, int):
            x = float(x)
        if isinstance(y, int):
            y = float(y)
        if isinstance(x, float) and isinstance(y, float):
            return Matrix3x3(Vector3(x,0,0), Vector3(0,y,0), Vector3(0,0,1))
        raise TypeError("Scale: int or float")

    def mult(self, other):
        if isinstance(other, Vector3):
            return Vector3(other.dot(self.r0), other.dot(self.r1), other.dot(self.r2))
        if isinstance(other, Matrix3x3):
            return Matrix3x3(
                Vector3(self.r0.dot(other.col(0)), self.r0.dot(other.col(1)), self.r0.dot(other.col(2))),
                Vector3(self.r1.dot(other.col(0)), self.r1.dot(other.col(1)), self.r1.dot(other.col(2))),
                Vector3(self.r2.dot(other.col(0)), self.r2.dot(other.col(1)), self.r2.dot(other.col(2)))
            )
        raise TypeError("mult: Vector3 or Matrix3x3")

    __mul__ = mult

    def col(self, index):
        if not isinstance(index, int):
            raise TypeError("col: int")
        if(index < 0 or index > 2):
            raise ValueError("col: [0,2]")
        return Vector3(self.r0[index], self.r1[index], self.r2[index])


    def toString(self):
        return "[" + str(self.r0) + ";" + str(self.r1) + ";" + str(self.r2) + "]"

    __str__ = toString