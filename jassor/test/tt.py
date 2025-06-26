

def main():
    patch_size = 1024

    points = []         # 1_000_000
    patched_points = {}

    for (x, y) in points:
        j, i = x // patch_size, y // patch_size
        if (j, i) not in patched_points:
            patched_points[(j, i)] = []
        patched_points[(j, i)].append((x, y))

    # 取了一个 patch
    pp = patched_points[(j, i)]
    patch = ...


def main2():
    x, y = point
    l, u, r, d = rect

    if l <= x < r and u <= y < d:
        pass


if __name__ == '__main__':
    main()
