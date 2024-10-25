from typing import Tuple, Union

from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, Multi


class Empty(Single, Multi):

    def buffer(self, distance: float):
        return self

    def standard(self):
        return self

    @property
    def geo(self) -> BaseGeometry:
        return None

    def clean(self):
        return self

    def offset(self, pos: Union[complex, Tuple[float, float]]):
        return self

    def scale(self, ratio: float):
        return self

    def rotate(self, degree: float):
        return self

    def flip_x(self, a: float):
        return self

    def flip_y(self, b: float):
        return self

    def flip(self, a: float, b: float):
        return self

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
        return [], []

    def sep_out(self):
        return []

    def sep_p(self):
        return []

    def copy(self):
        return self

    def __len__(self):
        return 0


Shape.EMPTY = Empty()
