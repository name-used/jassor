import math
from typing import List


def uniform_iter(T_len: int, I_len: int, max_gap: int) -> List[int]:
    """
    用于覆盖指定长度区间的函数，生成均匀分布的最小覆盖区间。

    参数：
    T_len (int): 需要被覆盖的总区间长度。例如 100。
    I_len (int): 每个覆盖区间的长度。例如 5。
    max_gap (int): 相邻覆盖区间起始位置的最大间距，确保覆盖的连续性。例如 3。

    返回：
    list: 包含每个覆盖区间起始位置的整数列表，以满足指定条件。
    """
    if I_len > T_len:
        return []
    
    remainder = (I_len - T_len) % max_gap
    if remainder == 0:
        return list(range(0, T_len-I_len + 1, max_gap))

    count = math.ceil((T_len - I_len) / max_gap)
    step = (T_len - I_len) / count

    # 步长数 + 原窗口0计数 => 总迭代量
    return [round(step * i) for i in range(count + 1)]
