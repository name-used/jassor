from abc import ABC
from typing import TypeVar, Generic


T = TypeVar('T')


# 超接口类
class Interface(ABC, Generic[T]):
    def method_b(self) -> T:
        return self


# 基类实现
class ImplBase(Interface['ImplBase']):
    def method_a(self) -> 'ImplBase':
        return self


# 具体实现类
class ImplementA(ImplBase[str]):
    pass


# 示例用法
impl = ImplementA()
pp = impl.method_a()
print(pp.method_a)
qq = impl.method_b()
print(qq.method_a)
