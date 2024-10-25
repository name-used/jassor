from abc import ABC
from typing import Tuple, Union


class Shape(ABC):
    """
    # 一个推荐的 C++ 实现方案: clipper
    自定义的 shapely 接口, 约定以下操作:
    1. 坐标运算:
    位移运算 -> offset, 参数 (x, y) 或 x+yj, 占用 左加运算符, 左减运算符 [+, -]
    缩放运算 -> scale, 参数 float, 占用 左乘运算符, 左除运算符 [*, /]
    * 旋转运算 -> rotate, 参数 float, 占用 左幂运算符 [**]
    * 镜像运算 -> flip_x, flip_y, flip, 参数 x, y, 表示函数对称轴(截距式), 不占用运算符
    2. 集合论运算:
    交集 -> inter, 占用 与运算符 [&]
    并集 -> union, 占用 或运算符 [|]
    * 异集 -> diff, 占用 异或运算符 [^]
    * 补集 -> comp, 交换内外轮廓, 占用 按位反运算符 [~]
    * 合集 -> merge, 令 other 附着至 self, 占用 左移运算符 [<<]
    * 差集 -> remove, 占用 右移运算符 [>>]
    3. 形态学运算:
    凸包络 -> convex, 不占用运算符
    密接矩形 -> mini_rect, 不占用运算符
    矩形域 -> region, 不占用运算符
    轮廓化简 -> simplify, 参数 int, 表示轮廓点密度, 不占用运算符
    轮廓平滑 -> smooth, 参数 int, 表示平滑程度, 不占用运算符
    4. 形态学属性
    形心 -> center, 返回 (x, y), 不占用运算符
    面积 -> area, 返回 float, 不占用运算符
    周长 -> perimeter, 返回 float, 不占用运算符
    矩形边界 -> bounds, 返回 (l, u, r, d), 不占用运算符
    5. 工程属性
    表示方式 -> reversed, 当前轮廓是正表示的还是负表示的(无穷远不属于轮廓 -> 正表示), 返回 bool, 不占用运算符, 受 补集运算支配
    正形 -> outer, 返回外轮廓(正表示, FULL 除外), 占用 自正运算符 [+]
    负形 -> inner, 返回内轮廓(正表示, FULL 除外), 占用 自反运算符 [-]
    6. 轮廓的分解
    内解 -> sep_inner, 返回 正形数组和负形数组, 不占用运算符
    外解 -> sep_outer, 多类型返回类型数组, 单类型返回自身构成的数组, 占用 迭代运算符 [iter]
    点解 -> sep_point, 返回类型结构数组, 参照具体类型说明, 不占用运算符
    7. 不支持的运算符:
    [
        加减乘除幂的右运算符 +, -, *, /, **
        取模运算符 abs, 取整运算符 round,
        比较运算符 <, <=, ==, !=, >=, >,
        赋值运算符 =, +=, -=, *=, /=, **=, //=, &=, |=, ^=, %=, <<=, >>=
        取余运算符 %, 整除运算符 //, 带余除法运算符 divmod
    ]
    8. 特殊形及操作
    空形 -> EMPTY, 同 [], 正形: EMPTY, 负形: FULL,内解: [], [FULL], 外解: [], 不可点解
    全形 -> FULL, 同 [FULL], 正形: FULL, 负形: EMPTY,内解: [FULL], [], 外解: [FULL], 不可点解
    """
    def offset(self, pos: Union[complex, Tuple[float, float]]):
        # 位移变换(原地的)
        raise NotImplementedError

    def scale(self, ratio: float):
        # 缩放变换(原地的)
        raise NotImplementedError

    def rotate(self, degree: float):
        # 旋转变换(原地的)
        raise NotImplementedError

    def flip_x(self, a: float):
        # 镜像变换, 对称轴 x=a (原地的)
        raise NotImplementedError

    def flip_y(self, b: float):
        # 镜像变换, 对称轴 y=b (原地的)
        raise NotImplementedError

    def flip(self, a: float, b: float):
        # 镜像变换, 对称轴 x/a + y/b = 1 (原地的)
        raise NotImplementedError

    def inter(self, other):
        # 集合论 交集运算 (创建新对象)
        raise NotImplementedError

    def union(self, other):
        # 集合论 并集运算 (创建新对象)
        raise NotImplementedError

    def diff(self, other):
        # 集合论 异集运算 (创建新对象)
        raise NotImplementedError

    def comp(self):
        # 集合论 补集运算 (创建新对象)
        raise NotImplementedError

    def merge(self, other):
        # 集合论 合集运算 (创建新对象)
        raise NotImplementedError

    def remove(self, other):
        # 集合论 差集运算 (创建新对象)
        raise NotImplementedError

    def simplify(self, tolerance: float):
        # 形态学 轮廓简化 (创建新对象)
        raise NotImplementedError

    def smooth(self, distance: float):
        # 形态学 轮廓平滑 (创建新对象)
        raise NotImplementedError

    def buffer(self, distance: float):
        # 形态学 轮廓腐蚀或膨胀 (创建新对象)
        raise NotImplementedError

    @property
    def convex(self):
        # 形态学 凸包络 (创建新对象)
        raise NotImplementedError

    @property
    def mini_rect(self):
        # 形态学 最小外接矩形 (创建新对象)
        raise NotImplementedError

    @property
    def region(self):
        # 形态学 最小坐标矩形 (创建新对象)
        raise NotImplementedError

    @property
    def center(self) -> Tuple[int, int]:
        # 形态学 形心
        raise NotImplementedError

    @property
    def area(self) -> float:
        # 形态学 面积
        raise NotImplementedError

    @property
    def perimeter(self) -> float:
        # 形态学 周长
        raise NotImplementedError

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        # 形态学 坐标边界
        raise NotImplementedError

    @property
    def reversed(self) -> bool:
        # 工程学 翻转表示标志
        raise NotImplementedError

    @property
    def outer(self):
        # 工程学 由外轮廓构成的多边形
        raise NotImplementedError

    @property
    def inner(self):
        # 工程学 由内轮廓构成的多边形, 若无内轮廓, 返回 EMPTY
        raise NotImplementedError

    def sep_in(self):
        # 工程学 将多边形分解为内轮廓多边形与外轮廓多边形
        raise NotImplementedError

    def sep_out(self):
        # 工程学 将多边形分解为多边形数组,其中每个多边形只含一个复连通区域
        raise NotImplementedError

    def sep_p(self):
        # 工程学 将多边形分解为坐标点列,这个点列只使用 python 原生的 list,tuple, 便于数据的传输和迁移
        raise NotImplementedError

    def copy(self):
        # 工程学 创建新对象
        raise NotImplementedError

    def standard(self):
        # 工程学 轮廓规范化 (创建新对象)
        raise NotImplementedError

    # 下列运算符均创建新对象
    def __add__(self, pos: Union[complex, Tuple[float, float]]):
        return self.copy().offset(pos)

    def __sub__(self, pos: Union[complex, Tuple[float, float]]):
        if isinstance(pos, complex):
            return self.copy().offset(-pos)
        else:
            return self.copy().offset((-pos[0], -pos[1]))

    def __mul__(self, ratio: float):
        return self.copy().scale(ratio)

    def __truediv__(self, ratio: float):
        assert ratio != 0, 'Could not div by 0!'
        return self.copy().scale(1 / ratio)

    def __pow__(self, degree: float):
        return self.copy().rotate(degree)

    def __and__(self, other):
        return self.copy().inter(other)

    def __or__(self, other):
        return self.copy().union(other)

    def __xor__(self, other):
        return self.copy().diff(other)

    def __invert__(self):
        return self.copy().comp()

    def __lshift__(self, other):
        return self.copy().merge(other)

    def __rshift__(self, other):
        return self.copy().remove(other)

    def __pos__(self):
        return self.copy().outer

    def __neg__(self):
        return self.copy().inner

    def __iter__(self):
        return iter(self.copy().sep_out())

    # 下列运算符均就地的修改对象
    def __iadd__(self, pos: Union[complex, Tuple[float, float]]):
        return self.offset(pos)

    def __isub__(self, pos: Union[complex, Tuple[float, float]]):
        if isinstance(pos, complex):
            return self.offset(-pos)
        else:
            return self.offset((-pos[0], -pos[1]))

    def __imul__(self, ratio: float):
        return self.scale(ratio)

    def __itruediv__(self, ratio: float):
        assert ratio != 0, 'Could not div by 0!'
        return self.scale(1 / ratio)

    def __ipow__(self, degree: float):
        return self.rotate(degree)

    def __iand__(self, other):
        return self.inter(other)

    def __ior__(self, other):
        return self.union(other)

    def __ixor__(self, other):
        return self.diff(other)

    def __ilshift__(self, other):
        return self.merge(other)

    def __irshift__(self, other):
        return self.remove(other)
