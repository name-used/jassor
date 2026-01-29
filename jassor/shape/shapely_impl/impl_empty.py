import io
import math
from typing import Tuple, Union

from .definition import Shape, NoSupportMethodException


class Empty(Shape):

    __slots__ = ()

    def is_valid(self):
        return True

    def buffer(self, distance: float):
        return self

    def standard(self):
        return self

    @property
    def geo(self):
        return None

    def clean(self):
        return self

    def offset(self, pos: Union[complex, Tuple[float, float]]):
        return self

    def scale(self, ratio: float, origin=0j):
        return self

    def rotate(self, degree: float, origin=0j):
        return self

    def flip_x(self, a: float):
        return self

    def flip_y(self, b: float):
        return self

    def flip(self, a: float, b: float):
        return self

    def is_joint(self, other) -> bool:
        return False

    def if_contain(self, other) -> bool:
        return False

    def inter(self, other):
        return self

    def union(self, other):
        return other

    def diff(self, other):
        return other

    def merge(self, other):
        return self

    def remove(self, other):
        return self

    def simplify(self, tolerance: float):
        return self

    def smooth(self, distance: float):
        return self

    @property
    def convex(self):
        return self

    @property
    def mini_rect(self):
        return self

    @property
    def region(self):
        return self

    @property
    def center(self) -> Tuple[int, int]:
        return 0, 0

    @property
    def area(self) -> float:
        return 0

    @property
    def perimeter(self) -> float:
        return 0

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return 0, 0, 0, 0

    @property
    def outer(self):
        return self

    @property
    def inner(self):
        return self

    def sep_in(self):
        return [], [Shape.FULL]

    def sep_out(self):
        return []

    def sep_p(self):
        # raise NoSupportMethodException('Shape Empty cannot be separated by point')
        return []

    def copy(self):
        return self

    def comp(self):
        return Shape.FULL

    @property
    def reversed(self) -> bool:
        return False

    def dumps(self) -> str:
        return 'Empty'

    def dumpb(self, f: io.BufferedWriter):
        return 'Empty', None, None


Shape.EMPTY = Empty()
