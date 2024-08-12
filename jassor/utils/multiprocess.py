from typing import TypeVar
from queue import Empty, Full
import multiprocessing


V = TypeVar('V')


class Process(multiprocessing.Process):
    def __init__(self, target: callable, args=()):
        super(Process, self).__init__(target=target, args=args)

    def start(self) -> None:
        super(Process, self).start()

    def run(self) -> None:
        super(Process, self).run()


class Queue(object):
    """
    这是一个简易的队列封装设计，占用基础类型 None 和 True
    建议通过字典格式传输控制信息和数据
    ready: 阻塞直到队列获得新元素，队列结束时返回 False
    is_end: 非阻塞判断队列是否结束时使用
    count: 调查队列运行情况时使用，不可靠，不建议用作条件判断
    push: 向队列中压入元素的方法
    pop: 从队列中取出元素的方法
    top: 查看队列头部元素的方法（请注意，该方法在线程/进程条件下表现不同，不同线程共享同一 top，而不同进程占据不同 top）
    end: 结束队列（目前不支持从底层结构上结束队列，要求队列结束时任务也跟着结束）
    """
    def __init__(self, maxsize: int = 0):
        self._top = True
        self.con = multiprocessing.Condition()
        self.que = multiprocessing.Queue(maxsize=maxsize)
        # 状态： 0, 1, 2
        # 0: 异常中止
        # 1: 正常运行
        # 2: 正常中止
        self.flag = multiprocessing.Value('i', 1)
        self._message = multiprocessing.Array('c', b' ' * 1000)

    def ready(self) -> bool:
        # 阻塞判定方法，当且仅当队列下一个元素已就绪时返回真
        return self.flag.value and self.top() is not None

    def is_end(self) -> bool:
        # 非阻塞判定方法，当队列已声明为不可用状态，或队列元素已取完并声明结束时返回真
        return not(self.flag.value and self._top is not None)

    def count(self) -> int:
        # 非阻塞方法，返回当前队列内的元素数量（不保证准确）
        return self.flag.value and (self.que.qsize() + (self._top is not True) - (self.flag.value & 0b10))

    def push(self, item: V) -> None:
        # 阻塞方法，向队列内推送值
        while self.flag.value == 1:
            # 正常运行状态，正常使用
            try:
                self.que.put(item, timeout=0.5)
                break
            except Full:
                pass
        else:
            if self.flag.value == 2:
                # 正常结束状态
                return
            # 异常结束状态，直接报错
            raise Closed(self.message())

    def top(self) -> V:
        # 阻塞独占方法，查看队列顶端元素值
        with self.con:
            while self.flag.value:
                # 正常运行状态，正常使用
                try:
                    if self._top is True:
                        self._top = self.que.get(timeout=0.5)
                    break
                except Empty:
                    if self.flag.value == 2:
                        # 正常结束状态
                        self._top = None
                        return None
            else:
                # 异常结束状态，直接报错
                raise Closed(self.message())
        return self._top

    def pop(self) -> V:
        # 阻塞独占方法，从队列中取值
        with self.con:
            item = self.top()
            if item is not None:
                self._top = True
        return item

    def message(self) -> str:
        return self._message.value.decode()

    def end(self, flag: bool = False, message: str = '') -> None:
        """
        结束队列，含两种结束方式，正常结束或异常结束
        flag == False: 正常结束，当前队列用完后不再接受新数据
        flag == True: 异常结束，立刻丢弃队列内元素，不再接受新数据
        """
        if flag:
            # 异常结束
            self.flag.value = 0
        else:
            # 正常结束
            self.flag.value = 2
            try:
                self.que.put(None, timeout=0.1)
                self.que.put(None, timeout=0.2)
            except Full:
                pass
        self._message.value = message.encode()


class Closed(BaseException):
    def __init__(self, message: str):
        super(Closed, self).__init__(message)


class QueueMessageException(BaseException):
    def __init__(self, message: str):
        super(QueueMessageException, self).__init__(message)
