from typing import List, Iterable, Union, Tuple
from functools import reduce
import numpy as np
import re


class Table(object):
    """
    这是一个统计表工具
    可以将它理解为 numpy 或 pandas 的扩展（但不使用 pandas）
    它解决的核心痛点是 numpy 不支持 key-word 索引
    考虑一项预测任务，其预测结果对应一族混淆矩阵，这族混淆矩阵可能是高维度数的
    例如：权重序列 weights 对 patches、batches、images 或者 groups 生成了相应的混淆矩阵，混淆矩阵本身又包含 pr、gt 各自类别的两个维度数
    其总体上构成了一个四维张量

    理论上，我们可以用各种各样的方法去存储这种数据结构，包括定义一个形如 [weight, image, pr, gt] 的 numpy 数组
    而问题在于，这个数组本身并不解释其所隶属维度数的含义，每当你切实需要访问其中的一些元素时，你总是需要通过额外的配置信息去确定待访问的索引
    这既麻烦，又容易出错，更不适合数据存储（你需要将相关的数据结构分别存储为配置信息和数据信息，且这二者之间的逻辑关系可能依赖代码去解析，以上三条缺失任意一条都会导致数据破损）

    本工具具备两项功能：
    1. 数据的结构化存储，一个表单就是一套数据，整存整读，不依赖额外配置项或代码逻辑
    2. 表意化索引读写，规避避免复杂的索引转换任务，强化代码可读性

    定义一个表单：
    # 给定维度参数, 可以用字典形式指定相应简写
    axis1 = {'r11': 'resnet-epoch-11', 'e17': 'efficient_net-epoch-17', 'c19': 'custom_net-epoch-19', ...}
    axis2 = ['patch-199', 'batch-21', 'image-7', 'group-train', ...]
    axis3 = {'bg': 'background', 'tg': 'target', 'nt': 'non-target'}
    axis4 = {'bg': 'background', 'tg': 'target', 'nt': 'non-target'}
    table = Table(axis1, axis2, axis3, axis4)

    向表单写入值：
    table[:, :, 'bg', 'bg'] = 0                     # 即： array[:, :, 0, 0] = 0
    table[:, :, ('bg', 'tg'), ('bg', 'tg')] = 0     # 即： array[:, :, 0:2, 0:2] = 0
    table[:, :, 0:2, (0, 1)] = [[0, 0], [0, 0]      # 即： array[:, :, 0:2, 0:2] = 0
    table['r11', 'patch-199'] = 0                   # 即： array[0, 0, :, :] = 0
    table[:, :, 'bg'] = {'bg':0, 'tg':0, 'nt': 0}   # 即： array[:, :, 0, :] = 0

    从表单取值：
    v = table['r11', 'patch-199', 'bg', 'bg']       # int
    v = table['r11', 'patch-199', ('bg', 'tg')]     # table[('bg', 'tg'), ('bg', 'tg', 'ng')]
    v = table['r11', 'patch-199'].array()           # array(3, 3)
    """

    def __init__(self, *key_names_list: List[str],
                 dtype: type = object,
                 data: np.ndarray = None,
                 key_sep: str = '-',
                 k_v_sep: str = ': ',):
        assert key_names_list is not None and len(key_names_list) > 0, 'There must be at least one key_name in params.'
        assert sum(len(names) <= 1 for names in key_names_list) == 0, 'Shape eq 0 or 1 is meaningless!'
        self.key_sep = key_sep
        self.k_v_sep = k_v_sep
        self.keys = key_names_list
        self.idx = [{n: i for i, n in enumerate(key_names)} for key_names in key_names_list]
        self.data = np.empty(shape=list(len(key_names) for key_names in key_names_list), dtype=dtype) \
            if data is None else data

    def __getitem__(self, items):
        # 先将输入规范化为元组
        if not isinstance(items, tuple):
            items = items,
        # 然后补齐缺失轴
        if len(items) < len(self.keys):
            items = *items, *(slice(None) for _ in range(len(self.keys) - len(items)))
        # 然后逐项翻译
        selects = []
        for pos, item in enumerate(items):
            # 若 iterable：逐项翻译
            # 若 slice：按规则翻译
            # 翻译 str： 参照idx
            # 翻译 int： 直取
            if isinstance(item, int) or isinstance(item, str):
                select = self.trans(pos, item),
            elif isinstance(item, Iterable):
                select = self.trans_iter(pos, item)
            elif isinstance(item, slice):
                select = self.trans_slice(pos, item)
            else:
                raise KeyError(f'Not supported type: {type(item)}')
            assert bool(select), f'Select nothing is meaningless! Check pos[{pos}] val[{item}]'
            selects.append(list(select))
        grids = self.select(selects)
        selected_data = self.data[grids]
        if all(isinstance(g, int) for g in grids):
            # Only when every axis has only one index, return single value
            if self.data.dtype != object:
                selected_data = selected_data.item()
            return selected_data
        else:
            # Else return Table
            return self.sub_table(selects, selected_data)

    def trans_str(self, pos: int, item: str) -> tuple:
        return self.idx[pos][item]

    def trans(self, pos: int, item: Union[int, str]) -> int:
        if item is None: return None
        assert isinstance(item, int) or isinstance(item, str), KeyError(f'Not supported type: {type(item)}')
        if isinstance(item, int): return item
        assert item in self.idx[pos], KeyError(f'Key "{item}" not in key-index-{pos + 1}')
        return self.idx[pos][item]

    def trans_slice(self, pos: int, item: slice) -> tuple:
        start = self.trans(pos, item.start)
        stop = self.trans(pos, item.stop)
        step = self.trans(pos, item.step)
        start = 0 if start is None else start
        stop = len(self.idx[pos]) if stop is None else stop
        step = 1 if step is None else step
        return tuple(range(start, stop, step))

    def trans_iter(self, pos: int, items: Iterable) -> tuple:
        return tuple(self.trans(pos, item) for item in items)

    def select(self, indexes: List[Tuple[int]]) -> np.ndarray:
        # 若索引指定唯一元素，则按单元素索引元组格式返回坐标
        if all(len(index) == 1 for index in indexes):
            return tuple(index[0] for index in indexes)
        # 若维度数少于2，可以直接返回
        if len(indexes) < 2:
            return tuple(indexes)
        # 否则先生成网格矩阵
        grids = np.meshgrid(*indexes)
        # 第一个维度和第二个维度需要转置 -> 我也不知道为什么
        axis = list(range(len(indexes)))
        axis[0] = 1
        axis[1] = 0
        # 然后返回 grid
        return tuple(grid.transpose(axis) for grid in grids)

    def sub_table(self, selects: List[Tuple[int]], selected_data: np.ndarray):
        names_list = [[self.keys[axis][index] for index in select] for axis, select in enumerate(selects)]
        names_list = [names for names in names_list if len(names) > 1]
        selected_data = np.squeeze(selected_data)
        return Table(*names_list, data=selected_data)

    def __setitem__(self, items, value):
        # 先将输入规范化为元组
        if not isinstance(items, tuple):
            items = items,
        # 然后补齐缺失轴
        if len(items) < len(self.keys):
            items = *items, *(slice(None) for _ in range(len(self.keys) - len(items)))
        # 然后逐项翻译
        selects = []
        # 检测是否包含序列 -> 这关系到返回值的类型
        iterable_flag = False
        for pos, item in enumerate(items):
            # 若 iterable：逐项翻译
            # 若 slice：按规则翻译
            # 翻译 str： 参照idx
            # 翻译 int： 直取
            if isinstance(item, int) or isinstance(item, str):
                select = self.trans(pos, item),
            elif isinstance(item, Iterable):
                select = self.trans_iter(pos, item)
            elif isinstance(item, slice):
                select = self.trans_slice(pos, item)
            else:
                raise KeyError(f'Not supported type: {type(item)}')
            selects.append(list(select))
        grids = self.select(selects)
        self.data[grids] = value

    def __str__(self):
        return self.str(type_repr=repr)

    def str(self, type_repr: callable) -> str:
        # 以 axis = 0 为 temp
        joints = [(key, [index]) for index, key in enumerate(self.keys[0])]
        # 逐 axis 做笛卡尔积
        for new_keys in self.keys[1:]:
            new_joints = []
            # 遍历 joints
            for last_key, last_indexes in joints:
                # 遍历 keys
                for new_index, new_key in enumerate(new_keys):
                    new_key = f'{last_key}{self.key_sep}{new_key}'
                    new_indexes = last_indexes + [new_index]
                    new_joints.append((new_key, new_indexes))
            joints = new_joints
        keys = [key for key, _ in joints]
        vals = [type_repr(self.data[tuple(indexes)]) for _, indexes in joints]
        content = '\n\t'.join(f'{key}{self.k_v_sep}{val}' for key, val in zip(keys, vals))
        return '{\n\t' + content + '\n}'

    def save(self, path: str, type_repr: callable = repr):
        with open(path, 'w') as f:
            # 首行存： 键值分隔符
            f.write(f'k-v-sep[{self.k_v_sep}]\n')
            # 次行存： 键分隔符
            f.write(f'key-sep[{self.key_sep}]\n')
            # 第三行存维度数
            f.write(f'axis{[len(key) for key in self.keys]}\n')
            # 接下来 len(axis) 行存每个维度的名称
            for key in self.keys:
                f.write(f'{key}\n')
            # 最后存数据
            f.writelines(self.str(type_repr=type_repr))

    @staticmethod
    def load(path: str, dtype: type = object, type_loader: callable = eval):
        with open(path, 'r') as f:
            lines = f.readlines()
        # 首行读： 键值分隔符
        # LINE_TEMP: k-v-sep[ANY_WORD]
        k_v_sep = re.compile(r'^\s*k-v-sep\[(.*)\]\s*$').findall(lines[0])[0]
        # Next line need env-python3.9
        # k_v_sep = lines[0].strip().removeprefix('k-v-sep[').removesuffix(']')

        # 次行读： 键分隔符
        # LINE_TEMP: key-sep[ANY_WORD]
        key_sep = re.compile(r'^\s*key-sep\[(.*)\]\s*$').findall(lines[1])[0]
        # Next line need env-python3.9
        # k_v_sep = lines[0].strip().removeprefix('k-v-sep[').removesuffix(']')

        # 三行读： 维度数
        # LINE_TEMP: axis[N1, N2, N3, ...]
        axis = re.compile(r'^\s*axis(.*)\s*$').findall(lines[2])[0]
        axis = eval(axis)
        # Next line need env-python3.9
        # k_v_sep = lines[0].strip().removeprefix('k-v-sep[').removesuffix(']')

        # 接下来 len(axis) 行读： 每个维度的名称
        # LINE_TEMP: ['', '', '', ...]
        key_names = [eval(line) for line in lines[3: 3 + len(axis)]]

        # 剩下的是封印在大括号中的键值对
        lines = lines[3 + len(axis) + 1: -1]

        # 行数与 axis 笛卡尔积不一致的，果断报错
        assert len(lines) == reduce(int.__mul__, axis), f'Lines-length not eq axis! check {axis} -> {len(lines)}'
        # 现在，是时候加载数据了
        table = Table(
            *key_names,
            dtype=dtype,
            key_sep=key_sep,
            k_v_sep=k_v_sep,
        )
        for line in lines:
            keys, value = line.strip().split(k_v_sep)
            keys = keys.split(key_sep)
            value = type_loader(value)
            table[tuple(keys)] = value
        return table


# path = '/media/totem_disk/totem/jizheng/breast_competation/recycle/test/save.txt'
#
# table = Table(['a', 'b', 'c'], ['aa', 'bb'], ['aaa', 'bbb', 'ccc'])
#
# table['a':'c', 'aa':'bb'] = np.ones(shape=(2, 1, 3))
#
# table.save(path=path)
#
# table2 = Table.load(path)
#
# print(table)
# print(table2)

# table['a', 'bb', 'ccc'] = 1
# table['a':'c', 'aa':'bb'] = np.ones(shape=(2, 1, 3))
# table['a', 'bb', :] = [object()] * 3
#
# x = table['a']
# y = table['a':'c', 'aa':'bb']
# z = table[:, :, :]
#
# print(x)
# print(y)
# print(z)

# print(table)
