from itertools import combinations
import numpy as np


n = 7
k = 4


def main():
    # 创建实验死亡矩阵
    # row 表示单只小鼠所选择的实验方案 2**n
    # col 表示毒药状态 C(n, 2)
    matrix = create_state_matrix()

    # 创建态映射冲突矩阵
    # row 表示不变
    # col 表示两毒药状态在当前方案条件下是否冲突
    matrix = join_matrix(matrix)

    for selects in combinations(list(range(2 ** n)), k):
        if matrix[selects, :].all(axis=0).any(): continue
        print(selects)
        return
    print('nothing')


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


main()
