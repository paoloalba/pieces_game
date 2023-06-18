import numpy as np

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Callable
from PIL import Image, ImageDraw
from typing_extensions import Self
from math import radians, degrees


@dataclass
class Point:
    x:float
    y:float

    def __repr__(self) -> str:
        return f"({self.x},{self.y})"
    
    def __add__(self, other:Self) -> Self:
        return Point(self.x+other.x, self.y+other.y)
    def __iadd__(self, other:Self) -> Self:
        self.x += other.x
        self.y += other.y
        return self
    def __sub__(self, other:Self) -> Self:
        return Point(self.x-other.x, self.y-other.y)
    def __isub__(self, other:Self) -> Self:
        self.x -= other.x
        self.y -= other.y
        return self

    def to_tuple(self):
        return (self.x, self.y)
    
    def translate(self, point:Self):
        self.x += point.x
        self.y += point.y
    
    def rotate(self, center:Self, angle:float):
        angle = radians(angle)
        s = np.sin(angle)
        c = np.cos(angle)

        self.x -= center.x
        self.y -= center.y

        xnew = self.x * c - self.y * s
        ynew = self.x * s + self.y * c

        self.x = xnew + center.x
        self.y = ynew + center.y

@dataclass
class Segment:
    p0: Point
    p1: Point
    length:float = field(init=False)
    coeff:float = field(init=False)
    points:Tuple = field(init=False)

    def __post_init__(self):
        self.length = np.sqrt((self.p1.x-self.p0.x)**2+(self.p1.y-self.p0.y)**2)
        if self.p1.x == self.p0.x:
            self.coeff = np.pi/2
        else:
            self.coeff = np.arctan((self.p1.y-self.p0.y) / (self.p1.x-self.p0.x))
        self.points = (self.p0, self.p1)

    def __repr__(self) -> str:
        return f"{self.p0}->{self.p1}"

    def to_tuple(self):
        return self.p0.to_tuple()+self.p1.to_tuple()
    
@dataclass
class Shape:
    points:List[Point]
    color_dict:Dict = field(default_factory=dict)
    num_points:int = field(init=False)
    white_col:Tuple = field(init=False, default=(255, 255, 255))
    segments:List[Segment] = field(init=False)

    def __post_init__(self):
        self.num_points = len(self.points)

        nw_list = []
        for iii in range(self.num_points):
            
            p0 = self.points[iii]
            if iii == self.num_points-1:
                p1 = self.points[0]
            else:
                p1 = self.points[iii+1]
            
            nw_list.append(Segment(p0,p1))
        self.segments = nw_list

    @staticmethod
    def create_empty_img():
        im = Image.new("RGB", (100, 100), Shape.white_col)
        return im

    #region Transformations

    def translate(self, delta:Point):
        for ppp in self.points:
            ppp.translate(delta)
        self.__post_init__()

    def rotate(self, center:Point, delta:float):
        for ppp in self.points:
            ppp.rotate(center, delta)
        self.__post_init__()

    #endregion

    def overlap(self, other:Self) -> bool:
        raise NotImplementedError()

    def combine(self, other:Self, gg:Tuple[int], pp:Tuple[int]) -> Self:
        g1 = self.segments[gg[0]]
        g2 = other.segments[gg[1]]
        pp = (g1.points[pp[0]], g2.points[pp[1]])
        other.translate(pp[0]-pp[1])
        angl = degrees(g2.coeff) - degrees(g1.coeff)
        other.rotate(pp[0], 180-angl)

    def draw(self, im:Image):
        draw = ImageDraw.Draw(im)

        for idx, sss in enumerate(self.segments):
            draw.line(sss.to_tuple(), fill=self.color_dict.get(idx, "black"))
