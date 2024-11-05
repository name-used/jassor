import time
import traceback
from typing import Iterable

import jassor.utils as J


def main():
    print('第一段程序描述正常运行用法')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序描述异常控制用法')
    demo2()


def demo1():
    que = J.Queue(5)
    pa = J.Process(target=producer, args=(que, [x+1 for x in range(10)]))
    pb = J.Process(target=consumer, args=(que, ))
    pa.start()
    pb.start()
    pa.join()
    pb.join()
    # 正常结束时，队列将持续运行到无任何元素输出，因此不同进程不共享结束状态
    print(que.is_end())
    # 但对队列的访问将明确这一结束状态
    print(que.top())
    print(que.is_end())


def demo2():
    que = J.Queue(5)
    pa = J.Process(target=producer, args=(que, [x for x in range(10)]))
    pb = J.Process(target=consumer, args=(que, ))
    # 为正常展示异常结束的情况，令消费者先执行代码并卡定在 que.pop 部分
    # 以免生产者报错太快导致消费者直接在 while 阶段退出
    pb.start()
    time.sleep(0.1)
    pa.start()
    pa.join()
    pb.join()
    print(que.is_end())


def producer(que: J.Queue, stream: Iterable):
    try:
        for data in stream:
            que.push({'cmd': 'do_process', 'arg': None, 'data': 1 / data})
        # 正常结束
        que.end(flag=False, message='success')
    except Exception as e:
        traceback.print_exc()
        # 异常结束
        que.end(flag=True, message=f'exception caused by {e}')


def consumer(que: J.Queue):
    while not que.is_end():
        try:
            item = que.pop()
            if item is None:
                print(f'normal que message {que.message()}')
            elif item['cmd'] == 'do_process':
                print(item['data'])
        except J.Closed:
            print('exception que message', que.message())


if __name__ == '__main__':
    main()
