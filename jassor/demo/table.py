import random

import numpy as np
import jassor.utils as J


def main():
    # print('第一段程序描述基本用法')
    # demo1()
    # input('输入任意字符以继续...')
    # print('第二段程序描述存写')
    # demo2()
    # input('输入任意字符以继续...')
    # print('第三段程序测试性能')
    demo3()     # 性能测试结论: 效率不高，不要拿来直接处理千万级的数据


def demo1():
    dimensions = [
        {'m1': 'model1', 'm2': 'model2', 'm3': 'model3'},
        ['bg', 'tg'],
        ['bg', 'tg'],
    ]
    # 可以用以下方式访问
    table = J.Table(*dimensions)
    table[...] = np.arange(12).reshape((3, 2, 2))   # 赋值
    # table = J.Table(*dimensions, data=np.arange(12).reshape((3, 2, 2)))   # 当然也可以这么做
    print(table)
    print(table['m1', 'bg', 'tg'])      # 用 key 访问
    print(table['model1', 'bg', 'tg'])  # 用 name 访问
    print(table[0, 0, 1])               # 用 index 访问
    print(table['m1': 'm3', 0, 0])      # 支持以 key/name/index 作序列索引，但注意：索引包含两端值
    print(table['m1', ..., 'tg'])       # 支持用 ... 省略维度
    print(table['m1', 'tg'])            # 所给维度数低于实体维度数时，默认省略后面的维度数


def demo2():
    dimensions = [
        {'m1': 'model1', 'm2': 'model2', 'm3': 'model3'},
    ]
    table = J.Table(*dimensions, data=np.arange(3) + 100)
    print([table.dumps()])
    print(J.Table.loads(table.dumps().split('\n')))
    with open('./table.txt', 'w') as f:
        table.dump(f)
    with open('./table.txt', 'r') as f:
        print(J.Table.load(f))
    with open('./table.pkl', 'wb') as f:
        table.dumpb(f)
    with open('./table.pkl', 'rb') as f:
        print(J.Table.loadb(f))


def demo3():
    rank = 7
    size_in_dim = 10
    table = J.Table(
        *[[f'd{i}_{j}' for j in range(size_in_dim)] for i in range(rank)],
        dtype=np.int64,
        data=np.arange(size_in_dim ** rank).reshape([size_in_dim] * rank),
    )

    T = J.TimerManager()
    with T['load_single']:
        collect = []
        for _ in range(100_000):
            dims = tuple(f'd{i}_{random.randint(0, 9)}' for i in range(rank))
            z = table[dims]
            collect.append(z)
    print('读取 100_000 次单条数据用时: ' + T.stamp(T.costs['load_single']))

    with T['load_small']:
        collect = []
        for _ in range(1_000):
            dims = tuple([
                f'd{i}_{j}' for j in random.sample(range(0, size_in_dim), random.randint(1, 3))
            ] for i in range(rank))
            sub_table = table[dims]
            collect.append(sub_table.data.sum())
    print('读取 1_000 次小批次数据用时: ' + T.stamp(T.costs['load_small']))

    with T['load_large']:
        collect = []
        for _ in range(10):
            dims = tuple([
                f'd{i}_{j}' for j in random.sample(range(0, size_in_dim), random.randint(7, 9))
            ] for i in range(rank))
            sub_table = table[dims]
            collect.append(sub_table.data.sum())
    print('读取 100 次大批次数据用时: ' + T.stamp(T.costs['load_small']))

    with T['write_single']:
        for p in range(100_000):
            dims = tuple(f'd{i}_{random.randint(0, 9)}' for i in range(rank))
            table[dims] = p
    print('写入 100_000 次数据用时: ' + T.stamp(T.costs['load_single']))

    with T['write_small']:
        for p in range(1_000):
            dims = tuple([
                f'd{i}_{j}' for j in random.sample(range(0, size_in_dim), random.randint(1, 3))
            ] for i in range(rank))
            table[dims] = p
    print('读取 100_000 次数据用时: ' + T.stamp(T.costs['load_small']))

    with T['write_large']:
        for p in range(10):
            dims = tuple([
                f'd{i}_{j}' for j in random.sample(range(0, size_in_dim), random.randint(7, 9))
            ] for i in range(rank))
            table[dims] = p
    print('写入 100_000 次数据用时: ' + T.stamp(T.costs['load_small']))


main()
