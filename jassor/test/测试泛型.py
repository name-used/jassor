from abc import ABC, abstractmethod
from typing import TypeVar, Generic

# 定义一个类型变量
T = TypeVar('T', bound='jassor.test.测试泛型2.ImplBase')


# 超接口类
class Interface(ABC, Generic[T]):
    pass
