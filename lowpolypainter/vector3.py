

class Vector3(object):

    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @staticmethod
    def Vector2(x, y):
        return Vector3(x, y, 0)

    @staticmethod
    def Point2(x, y):
        return Vector3(x, y, 1)

    def dot(self, other):
        if isinstance(other, Vector3):            
            return self.x * other.x + self.y * other.y + self.z * other.z
        raise TypeError("dot: Vector3")
    
    def mult(self, other):
        if isinstance(other, int):
            other = float(other)
        if isinstance(other, float):
            return Vector3(self.x * other, self.y * other, self.z * other)
        if isinstance(other, Vector3):            
            return self.dot(other)
        raise TypeError("mult: int, float or Vector3")

    __mul__ = mult
    __rmul__ = __mul__

    def add(self, other):
        if isinstance(other, Vector3):            
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError("add: Vector3")

    __add__ = add
    __radd__ = __add__

    def sub(self, other):
        if isinstance(other, Vector3):            
            return self.add(other.mult(-1.0))
        raise TypeError("sub: Vector3")

    __sub__ = sub
