import numpy as np

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Callable
from PIL import Image, ImageDraw
from typing_extensions import Self
from math import radians, degrees
from copy import deepcopy
from itertools import product
from IPython.display import display
from shapely import Polygon, affinity
from shapely.ops import cascaded_union

class ShapesIntersects(Exception):
    ...

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
    polygon:Polygon = field(init=False)

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

        self.polygon = Polygon([(sss.x, -sss.y) for sss in self.points])

    @staticmethod
    def create_empty_img():
        im = Image.new("RGB", (500, 500), Shape.white_col)
        return im

    #region Transformations

    def translate(self, delta:Point):
        aff_p = affinity.translate(self.polygon, xoff=delta.x, yoff=-delta.y)
        for ppp in self.points:
            ppp.translate(delta)
        self.__post_init__()
        self.polygon = aff_p

    def rotate(self, center:Point, delta:float):
        for ppp in self.points:
            ppp.rotate(center, delta)
        self.__post_init__()

    #endregion

    @staticmethod
    def rotate_list(l:List, n:int):
        return l[n:] + l[:n]
    
    def center_point_list(self, center_point:Point):
        cnt_idx = self.points.index(center_point)
        self.points = Shape.rotate_list(self.points, cnt_idx)
        self.__post_init__()
        nw_dict = {}
        for kkk, vvv in self.color_dict.items():
            if kkk+cnt_idx > self.num_points-1:
                nw_dict[kkk+cnt_idx-self.num_points] = vvv
            else:
                nw_dict[kkk+cnt_idx] = vvv
        self.color_dict = nw_dict

    def combine(self, other:Self, gg:Tuple[int], pp:Tuple[int]) -> Self:

        s1 = deepcopy(self)
        s2 = deepcopy(other)

        g1 = s1.segments[gg[0]]
        g2 = s2.segments[gg[1]]

        pp = (g1.points[pp[0]], g2.points[pp[1]])

        center_point = pp[0]
        print(g1,g2,center_point)

        s2.translate(pp[0]-pp[1])
        print(g1,g2,center_point)
        angl = degrees(g2.coeff) - degrees(g1.coeff)
        print(angl)
        s2.rotate(center_point, 180-angl)
        print(g1,g2,center_point)

        if s1.intersects(s2):
            raise ShapesIntersects("shapes intersect")

        return s1, s2

        nw_points = []
        nw_points.append(center_point)

        s1.center_point_list(center_point)
        s2.center_point_list(center_point)

        l_list = s1.points
        r_list = s2.points

        if g1.length > g2.length:
            nw_points.extend(s2.points[::-1][:-1])
            nw_points.extend(s1.points[1:])
        else:
            nw_points.extend(s1.points[::-1][:-1])
            nw_points.extend(s2.points[1:])
        
        return Shape(nw_points)

    def draw(self, im:Image):
        draw = ImageDraw.Draw(im)

        for idx, sss in enumerate(self.segments):
            draw.line(sss.to_tuple(), fill=self.color_dict.get(idx, "black"))

    def intersects(self, other:Self) -> bool:
        return self.polygon.overlaps(other.polygon)

    def calculate_centroid(self):
        return Point(np.mean([ppp.x for ppp in self.points]), np.mean([ppp.y for ppp in self.points]))

    @staticmethod
    def show_all(shape_list:List[Self]):
        im = Shape.create_empty_img()
        for sss in shape_list:
            sss.draw(im)
        display(im)

    def show(self):
        im = Shape.create_empty_img()
        self.draw(im)
        display(im)

    def center(self, center_point:Point):
        self.translate(center_point-self.calculate_centroid())

    def is_t_shape(self):
        True
    
    def get_all_combinations(self, other:Self):
        cmb_l = []

        for sss, ppp in product(product(range(self.num_points), range(other.num_points)), product(range(2), range(2))):
            try:
                cmb_l.append(self.combine(other, sss, ppp))
            except ShapesIntersects:
                print("Intersection", sss, ppp)
            except Exception as excp:
                print(sss, ppp)
                raise excp
        
        return cmb_l


