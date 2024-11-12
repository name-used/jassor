import itertools
import json
import pickle
from typing import List, Iterable, Union, Tuple, Dict, TextIO, BinaryIO
import numpy as np


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

    本工具具备三项功能：
    1. 数据的结构化存储，一个表单就是一套数据，整存整读，不依赖额外配置项或代码逻辑
    2. 表意化索引读写，规避避免复杂的索引转换任务，强化代码可读性
    3. 强化数据可读性，有时候使用代码显示数据会显得很麻烦很啰嗦，本工具支持直接阅读原始数据

    定义一个表单：
    给定维度参数, 可以用字典形式指定相应简写
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

    表单存取
    table.set_key_sep('#')  # 不同维度键之间的分割符
    table.set_kv_sep(':')   # 键与数值之间的分割符
    print(table.dumps())    # 直接打印为字符串序列，依赖 sep
    table.dump(TextIO)   # 存成可读文档形式，依赖 sep
    table.dumpb(BinaryIO)  # dumpb 不依赖 sep
    table = Table.loads(table_str)
    table = Table.load(TextIO)
    table = Table.loadb(BinaryIO)
    """

    def __init__(self, *dimensions: Union[List[str], Dict[str, str]],
                 dtype: Union[np.dtype, type] = object,
                 data: np.ndarray = None,
                 key_sep: str = '-',
                 k_v_sep: str = ': ',):
        self.rank = len(dimensions)
        self.size_in_dims = [len(dimension) for dimension in dimensions]
        self.key_sep = key_sep
        self.k_v_sep = k_v_sep
        self.dim_keys = []
        self.dim_names = []
        for dimension in dimensions:
            if isinstance(dimension, List):
                self.dim_keys.append(dimension)
                self.dim_names.append(dimension)
            else:
                self.dim_keys.append(list(dimension.keys()))
                self.dim_names.append(list(dimension.values()))
        self.key_index_map = [{key: i for i, key in enumerate(dim_key)} for dim_key in self.dim_keys]
        self.name_index_map = [{name: i for i, name in enumerate(dim_name)} for dim_name in self.dim_names]

        self.data = np.empty(shape=self.size_in_dims, dtype=dtype) if data is None else data

    def __getitem__(self, items):
        select_indexes_in_dim, grids = self.trans_item_args(items)
        selected_data = self.data[grids]
        if all(isinstance(g, int) for g in grids):
            return selected_data.item()
        else:
            return self.sub_table(select_indexes_in_dim, selected_data)

    def __setitem__(self, items, value):
        select_indexes_in_dim, grids = self.trans_item_args(items)
        self.data[grids] = value

    def __str__(self):
        return '{\n' + self.str(type_repr=repr).replace('\n', '\n\t') + '\n}'

    def dump(self, f: TextIO):
        f.write(self.dumps())

    def dumpb(self, f: BinaryIO):
        dimensions = [
            dict(zip(dim_key, dim_name))
            for dim_key, dim_name in zip(self.dim_keys, self.dim_names)
        ]
        pickle.dump({
            'dimensions': dimensions,
            'data': self.data,
        }, f)

    def dumps(self, type_repr: callable = repr):
        dtype = f'dtype[{self.data.dtype}]'
        kv_sep = f'k-v-sep[{self.k_v_sep}]'
        key_sep = f'key-sep[{self.key_sep}]'
        dimensions = [
            dict(zip(dim_key, dim_name))
            for dim_key, dim_name in zip(self.dim_keys, self.dim_names)
        ]
        content = self.str(type_repr=type_repr)
        return f'{dtype}\n{kv_sep}\n{key_sep}\n' + '\n'.join([json.dumps(dimension) for dimension in dimensions]) + content

    def str(self, type_repr: callable) -> str:
        dim_keys = [[(index, key) for index, key in enumerate(dim_key)] for dim_key in self.dim_keys]
        cartesian = list(itertools.product(*dim_keys))
        cartesian = [
            (   # indexes, keys
                [item[0] for item in items],
                [item[1] for item in items]
            )
            for items in cartesian
        ]
        lines = [
            f'{self.key_sep.join(keys)}{self.k_v_sep}{type_repr(self.data[tuple(indexes)])}'
            for indexes, keys in cartesian
        ]
        return '\n'.join(lines)

    @staticmethod
    def load(f: TextIO, type_loader: callable = json.loads):
        return Table.loads(f.readlines(), type_loader=type_loader)

    @staticmethod
    def loadb(f: BinaryIO):
        data = pickle.load(f)
        return Table(*data['dimensions'], data=data['data'])

    @staticmethod
    def loads(lines: List[str], type_loader: callable = json.loads):
        head = {}
        for head_pos, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            # 前三行是表头，接下来一行是维度定义，再往后是数据项
            if line.startwith('dtype[') and line.endwith(']'):
                head['dtype'] = line[line.find('[') + 1:-1]
            elif line.startwith('k-v-sep[') and line.endwith(']'):
                head['kv_sep'] = line[line.find('[') + 1:-1]
            elif line.startwith('key-sep') and line.endwith(']'):
                head['key_sep'] = line[line.find('[') + 1:-1]
            else:
                head['dimensions'] = json.loads(''.join(lines[head_pos]))
                head['head_pos'] = head_pos
                break
        assert all(v in head for v in ['dtype', 'head_pos', 'kv_sep', 'key_sep', 'rank', 'dimensions'])

        # 现在，是时候加载数据了
        table = Table(
            **head['dimensions'],
            dtype=np.dtype(head['dtype']),
            key_sep=head['key_sep'],
            k_v_sep=head['kv_sep'],
        )
        for line in lines[head['head_pos'] + 1]:
            line = line.strip()
            if not line: continue
            keys, value = line.split(head['kv_sep'])
            keys = keys.split(head['key_sep'])

            value = type_loader(value)
            table[tuple(keys)] = value
        return table

    def trans_item_args(self, items):
        # 先将输入规范化为元组
        if not isinstance(items, tuple):
            items = items,
        # 然后补齐缺失轴
        if len(items) < self.rank:
            items = *items, *(slice(None) for _ in range(self.rank - len(items)))
        # 然后逐项翻译
        select_indexes_in_dim = []
        for dim_index, item in enumerate(items):
            # 若 iterable：逐项翻译
            # 若 slice：按规则翻译
            # 翻译 str： 参照idx
            # 翻译 int： 直取
            if item is None:
                item = slice(None)
            if isinstance(item, int) or isinstance(item, str):
                select = self.trans(dim_index, item, 0)
            elif isinstance(item, Iterable):
                select = self.trans_iter(dim_index, item)
            elif isinstance(item, slice):
                select = self.trans_slice(dim_index, item)
            else:
                raise KeyError(f'Not supported type: {type(item)}')
            # assert bool(select), f'Select nothing is meaningless! Check dim_index[{dim_index}] val[{item}]'
            select_indexes_in_dim.append(select)
        grids = self.select(select_indexes_in_dim)
        return select_indexes_in_dim, grids

    def trans(self, dim_index: int, item: Union[int, str], default: int) -> int:
        if item is None: return default
        if isinstance(item, int): return item
        if item in self.key_index_map[dim_index]: return self.key_index_map[dim_index][item]
        assert item in self.name_index_map[dim_index], KeyError(f'Key "{item}" not in dim_index-{dim_index}')
        return self.name_index_map[dim_index][item]

    def trans_slice(self, dim_index: int, item: slice) -> tuple:
        start = self.trans(dim_index, item.start, 0)
        stop = self.trans(dim_index, item.stop, self.size_in_dims[dim_index])
        step = self.trans(dim_index, item.step, 1)
        return tuple(range(start, stop, step))

    def trans_iter(self, dim_index: int, items: Iterable) -> tuple:
        return tuple(self.trans(dim_index, item, 0) for item in items)

    @staticmethod
    def select(select_indexes_in_dim: List[Tuple[int]]) -> Tuple[np.ndarray]:
        # # 若索引指定唯一元素，则按单元素索引元组格式返回坐标
        # if all(len(index) == 1 for index in indexes):
        #     return tuple(index[0] for index in indexes)
        # # 若维度数少于2，可以直接返回
        # if len(indexes) < 2:
        #     return tuple(indexes)
        # 否则先生成网格矩阵
        grids: List[np.ndarray] = np.meshgrid(*select_indexes_in_dim, indexing='ij')
        # 然后返回 grid
        return tuple(grids)

    def sub_table(self, select_indexes_in_dim: List[Tuple[int]], selected_data: np.ndarray):
        names_list = [
            # 从命名空间中选取相关命名
            [self.dim_names[dim_index][index] for index in select_indexes]
            for dim_index, select_indexes in enumerate(select_indexes_in_dim)
            # 如果某一个维度里选定了一个确定的维度数，那就没必要保留这个维度的名称了，所以用 tuple 过滤， tuple 表示多选
            if isinstance(select_indexes, tuple)
        ]
        return Table(*names_list, data=selected_data)
