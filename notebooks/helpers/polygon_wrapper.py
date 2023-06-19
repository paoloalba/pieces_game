from shapely import Polygon, affinity, Point, LineString
from shapely.ops import unary_union
from dataclasses import dataclass, field
from typing import List, Tuple
from typing_extensions import Self
from math import radians, degrees
import numpy as np
from itertools import product

class ShapesIntersects(Exception):
    ...

@dataclass
class WrpShape:
    points:List[Point]
    polygon:Polygon = field(init=False)
    num_points:int = field(init=False)

    def __post_init__(self):
        self.polygon = Polygon(self.points)
        self.points = list(self.polygon.exterior.coords)
        self.num_points = len(self.points)

    @staticmethod
    def calcolate_angle(p1, p2):
        if p1[0] == p2[0]:
            return degrees(np.pi / 2)
        else:
            return degrees(np.arctan((p1[1]-p2[1]) / (p1[0]-p2[0])))

    def combine(self, other:Self, p_self:Tuple, p_other:Tuple):
        self_idx = self.points.index(p_self)
        if self_idx == self.num_points:
            next_self_idx = 0
        else:
            next_self_idx = self_idx +1

        other_idx = other.points.index(p_other)
        if other_idx == other.num_points:
            next_other_idx = 0
        else:
            next_other_idx = other_idx +1

        src_p = self.polygon
        src_1 = self.points[self_idx]
        src_2 = self.points[next_self_idx]

        dst_1 = other.points[other_idx]
        dst_2 = other.points[next_other_idx]

        dx = (src_1[0]- dst_1[0], src_1[1]- dst_1[1])
        src_alfa = WrpShape.calcolate_angle(src_1, src_2)
        dst_alfa = WrpShape.calcolate_angle(dst_1, dst_2)

        allo = []
        allo.append(-(src_alfa+dst_alfa))
        allo.append(src_alfa-dst_alfa)

        angle = min(allo, key=abs)

        dst_p = other.polygon
        dst_p = affinity.translate(dst_p, xoff=dx[0], yoff=dx[1])
        dst_p = affinity.rotate(dst_p, angle=angle, origin=src_1)

        if src_p.overlaps(dst_p):
            raise ShapesIntersects()

        nw_sh = unary_union([src_p, dst_p])
        return nw_sh

        return WrpShape(list(nw_sh.exterior.coords))
        
    def get_all_combinations(self, other:Self):
        cmb_l = []

        overlap_cmb = []
        for sss, ddd in product(self.points, other.points):
            try:
                cmb_l.append(self.combine(other, sss, ddd))
            except ShapesIntersects:
                print("Intersection", sss, ddd)
            except Exception as excp:
                print(sss, ddd)
                raise excp
        
        return cmb_l




