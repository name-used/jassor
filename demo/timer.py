import time
import multiprocessing
from utils import Timer, TimerManager


def main():
    print('第一段程序描述with块用法')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序描述注解用法')
    demo2()
    input('输入任意字符以继续...')
    print('第三段程序描述多进程用法')
    demo3()


def demo1():
    T = TimerManager()
    # 使用 with 块语法统计代码用时
    with T['demo1_1']:
        wait(0.2)
        # 可以嵌套使用
        with T['demo1_2']:
            wait(0.1)
        # 可以重复使用
        with T['demo1_2']:
            wait(0.1)
        # 但不要在嵌套中重复使用外部嵌套用名
        # with T['demo1_1']:
        #     wait(0.1)
        # 可以用于非高频循环代码
        for i in range(100_000):
            with T['demo1_3']:
                x = i ** 6
    # 统计和显示用时
    for name, cost in T.costs.items():
        print(f' -> mission[{name}] cost time [{T.stamp(cost)}]')


def demo2():
    container = {}
    TimerManager.regist_container('share', container)
    # 使用注解方式统计用时时，应当在 TimerManager 中注册计时容器
    # 以下两种方式均可使用
    # T = TimerManager(container=container)
    T = TimerManager(container='share')
    with T['demo2_1']:
        wait(0.1)
    test()
    # 统计和显示用时
    # 以下两种方式均可使用
    # for name, cost in T.costs.items():
    for name, cost in container.items():
        print(f' -> mission[{name}] cost time [{T.stamp(cost)}]')


def demo3():
    share = multiprocessing.Manager().dict()
    group = []
    T = TimerManager(container=share)
    with T['demo3_all']:
        for i in range(20):
            key = str(i) if i < 10 else 'same'
            process = multiprocessing.Process(target=my_process, args=(key, i % 10 * 0.1, share))
            group.append(process)
        for g in group:
            g.start()
        for g in group:
            g.join()
    # time.sleep(1)
    for name, cost in share.items():
        print(f' -> mission[{name}] cost time [{TimerManager.stamp(cost)}]')


@Timer(key='demo2_2', container='share')
def test():
    # 使用注解方式统计用时
    wait(0.2)


def my_process(key: str, t: float, share: dict):
    # 需要注意的是，多进程时间统计效率较低，且不能保证准确性
    T = TimerManager(container=share)
    with T[f'demo3_{key}']:
        wait(t)
        # 大量进程同时写入共享变量会引起幻觉现象，此现象建议在编程中避免，本工具不予解决
        # wait(1)
        # 幻觉现象产生机制如下：
        # process_1: load << share
        # process_2: load << share
        # process_2: write >> share
        # process_1: write >> share
        # 由于 process_1 所加载的 share 数据未计算 process_2 统计
        # 而 process_1 的写入在 process_2 写入之后
        # 因此 process_2 的写入会完全丢失，导致时间统计异常


def wait(t: float) -> None:
    time.sleep(t)


if __name__ == '__main__':
    main()
