import math
from itertools import combinations
import numpy as np


# 这套思路到头了，解决不了富裕仗问题
n = 7
k = 5


def main():
    # 创建实验死亡矩阵
    # row 表示单只小鼠所选择的实验方案 2**n
    # col 表示毒药状态 C(n, 2)
    state_matrix = create_state_matrix()
    row, col = state_matrix.shape

    # 创建态映射冲突矩阵
    # row 表示不变
    # col 表示两毒药状态在当前方案条件下是否冲突
    conflict_matrix = join_matrix(state_matrix)

    # 评价信息量
    target_info = math.log2(n * (n-1) // 2)
    information = []
    for r in range(row):
        # 死亡事件所对应的结果数
        s = sum(state_matrix[r, :])
        # 当前实验所对应的香农信息熵 H(X)
        # H(X) = sum: -P(x) * log_a P(x)
        # 右式中：-log_a P(x) 描述出现此结果所蕴含的信息量
        # sum: P(x) 是对全部结果的加权和
        p = s / col
        if p == 0 or 1-p == 0:
            x = 0
        elif 1 + math.log2(max(p, 1-p)) > k - target_info:
            # 如果单次实验所对应的最低信息量会直接导致实验不达标，则该次实验的平均信息量直接记为 0
            x = 0
        else:
            # 实验所对应的平均信息量
            x = -p * math.log2(p) - (1-p) * math.log2(1-p)
            # 实验所对应的最差信息量，但用这个得出的结论是错的
            # x = - math.log2(max(1-p, p))
        information.append(x)
    for i, info in enumerate(information):
        print(bin(i), sum(state_matrix[i, :]), info)

    # 评估一下这个结果对不对
    # [98, 196, 28, 81, 146, 7]
    # print(conflict_matrix[[98, 196, 28, 81, 146, 7], :].all(axis=0).any())
    # return

    # 依据信息量排序
    row_idx = np.argsort(information)
    # row_idx = row_idx[::-1]
    # 试试过滤
    # 按正序排列，过滤 0.9，可以找到 V(8, 6) 的答案 [98, 196, 28, 81, 146, 7]
    # 按逆序排列，不需要过滤，可以找到 V(8, 7) 的答案 [132, 5, 6, 160, 144, 42, 25]
    # 随便正序逆序，不要开过滤，可以验证 V(8, 5) == False
    row_idx = [row_id for row_id in row_idx if information[row_id] > 0]

    # 用信息量筛查当前选择是否有可能达标（非法筛查）
    # 用态映射冲突矩阵检查是否满足要求（合法筛查）
    results = loop(information, target_info, row_idx, conflict_matrix, k, [])
    print(results)


def loop(information, target_info, row_idx, conflict_matrix, limits, selects):
    # 如果 limits 告罄，则依据 conflict_matrix 判断可行性
    if limits == 0:
        if conflict_matrix[selects, :].all(axis=0).any(): return False
        return selects
    # 逐行筛查信息量
    for i, r in enumerate(row_idx):
        # if information[r] < 0.9:
        #     continue
        # 如果选择当前行会导致信息量无论如何都不可能达标，就直接过滤
        if information[r] + limits - 1 < target_info:
            continue
        # 否则可以继续搜索
        result = loop(information, target_info - information[r], row_idx[i+1:], conflict_matrix, limits-1, selects + [r])
        # 有一个结果就说明行
        if result:
            return result
    # 都没有就意味着不行
    return False


def create_state_matrix():
    row = 2**n
    col = n * (n-1) // 2
    col_items = combinations(list(range(n)), 2)

    matrix = np.zeros((row, col), dtype=bool)
    for c, (p, q) in enumerate(col_items):
        for r in range(row):
            matrix[r, c] = r & (1 << p) | r & (1 << q)

    return matrix


def join_matrix(matrix):
    row = 2**n
    col = n * (n-1) // 2
    col_items = combinations(list(range(col)), 2)
    col = col * (col-1) // 2

    new_matrix = np.zeros((row, col), dtype=bool)
    for c, (p, q) in enumerate(col_items):
        for r in range(row):
            new_matrix[r, c] = matrix[r, p] == matrix[r, q]

    return new_matrix


def main_backup():
    # 创建实验死亡矩阵
    # row 表示单只小鼠所选择的实验方案 2**n
    # col 表示毒药状态 C(n, 2)
    state_matrix = create_state_matrix()

    # 创建态映射冲突矩阵
    # row 表示不变
    # col 表示两毒药状态在当前方案条件下是否冲突
    conflict_matrix = join_matrix(state_matrix)

    # 用状态矩阵筛查信息量是否达标（非法筛查）
    # 用态映射冲突矩阵检查是否满足要求（合法筛查）
    results = loop(state_matrix, conflict_matrix, k, [], 0)
    print(results)

    # 下面这一套也能用，但只能计算临界否定形式

    # # 分析信息量，信息量不达标直接 pass
    # possibilities = []
    # for r in range(row):
    #     s = sum(state_matrix[r, :])
    #     # 这个计算的就是信息量，实际上不必用，但 ppt 要提一嘴
    #     # x = math.log2(1 / max(s / col, 1 - s / col))
    #     if max(s, col-s) <= 2**(k-1):
    #         possibilities.append(r)
    #         print(math.log2(col / max(s, col-s)))
    # for p in possibilities:
    #     print(bin(p), )

    # 创建态映射冲突矩阵
    # row 表示不变
    # col 表示两毒药状态在当前方案条件下是否冲突
    # conflict_matrix = join_matrix(state_matrix)

    # # 对单次实验信息量达标的组合检查态映射冲突
    # for selects in combinations(possibilities, k):
    #     if matrix[selects, :].all(axis=0).any(): continue
    #     print(selects)
    #     return
    # print('nothing')


def loop_backup(state_matrix, conflict_matrix, limits, selects, row_start):
    # 如果 limits 告罄，则依据 conflict_matrix 判断可行性
    if limits == 0:
        if conflict_matrix[selects, :].all(axis=0).any(): return False
        return selects
    # 寻找当前不确定性最大的状态组合作为信息量筛查模板
    temp = find_temp(state_matrix, selects)
    # 逐行筛查信息量
    row, col = state_matrix.shape
    for r in range(row_start, row):
        sample = state_matrix[r, :]
        num = max((temp & sample).sum(), (temp & ~sample).sum())
        if num > 2 ** (limits-1):
            # 此条件不达标意味着选择 r 后剩余状态数量大于可区分总量，因此不必继续搜索
            continue
        # 否则可以继续搜索
        result = loop(state_matrix, conflict_matrix, limits-1, selects + [r], r+1)
        # 有一个结果就说明行
        if result:
            return result
    # 都没有就意味着不行
    return False


def find_temp(state_matrix, selects):
    # 寻找当前不确定性最大的状态组合作为信息量筛查模板 —— 简化版
    state_counts = np.zeros(2**len(selects), dtype=np.int32)
    row, col = state_matrix.shape
    state_mark = np.zeros(col, dtype=np.int32)
    for i, s in enumerate(selects):
        state_mark += (1 << i) * state_matrix[s, :]
    for c in range(col):
        state_counts[state_mark[c]] += 1
    state = state_counts.argmax()
    return state_mark == state


def find_temp_standard(state_matrix, selects):
    # 寻找当前不确定性最大的状态组合作为信息量筛查模板
    state_counts = np.zeros(2**len(selects), dtype=np.int32)
    row, col = state_matrix.shape
    state_mark = np.zeros(col, dtype=np.int32)
    for i, s in enumerate(selects):
        state_mark += (1 << i) * state_matrix[s, :]
    for c in range(col):
        state_counts[state_mark[c]] += 1
    state = state_counts.argmax()
    return state_mark == state


main()
