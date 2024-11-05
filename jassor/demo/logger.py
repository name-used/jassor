import time
from typing import TextIO
import sys
import multiprocessing
import jassor.utils as J


def main():
    print('第一段程序描述基本用法')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序描述文件输出用法')
    demo2()


def demo1():
    L = J.Logger(level=J.Logger.DEBUG)
    # 按级别决定是否输出日志
    L.step('message 1')
    L.debug('message 2')
    L.info('message 3')
    L.warn('message 4')
    # 用 tab 块控制输出格式
    for i in range(2):
        L1 = L.tab()
        L1.info(f'loop {i}')
        for j in range(3):
            time.sleep(0.1)
            L1.tab().info(f'{i} {j}')
    # 用 with 块记录信息，并就地计算和输出单词代码块运行用时
    with L['log_name'] as L1:
        L1.info('message in block')
        time.sleep(0.5)


def demo2():
    # file 可以是任意 TextIO
    L = J.Logger(file=sys.stderr)
    L.info('message')
    L.close()
    # 下列两种方式等价
    L = J.Logger(file='./log1.txt')
    L.info('message')
    L.close()
    with open('./log2.txt', 'a') as f:
        L = J.Logger(file=f)
        L.info('message')
        L.close()
    # 对于更一般的管道，用 IOWrapper 包装一下依旧可以输出
    receiver, sender = multiprocessing.Pipe(False)
    sender = J.IOWrapper(write_func=sender.send, flush_func=None, close_func=sender.close)
    process = multiprocessing.Process(target=subprocess, args=(sender,))
    process.start()
    process.join()
    print(receiver.recv())


def subprocess(pipe: TextIO):
    L = J.Logger(file=pipe)
    L.info('sender message')
    L.close()


if __name__ == '__main__':
    main()
