"""shape module: Contains class Shape,Square,and Circle，其他图形"""
class Shape:
    """Shape class: has method move"""
    def __init__(self,x,y):
        self.x = x
        self.y =y
    def move(self,deltaX,deltaY):
        self.x=self.x+deltaX
        self.y=self.y+deltaY

class Square(Shape):
    """Square class inherit from shape"""
    def __init__(self,x,y,side=1):
        Shape.__init__(self,x, y)
        self.side=side

class Circle(Shape):
    """Circle class: inherit from shape and has method circle"""
    pi=3.14
    def __init__(self,r, x, y):
        Shape.__init__(self,x, y)
        self.radius= r
    def area(self):
        """circle fun"""
        return self.radius*self.radius*self.pi
    def __str__(self):
        return f"{self.radius} circles"
def _add():
    print("hello")
    return("hello")