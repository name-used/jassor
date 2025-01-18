def main():
    # 输入：三个整数
    # 第一个为质数，表示p
    # 第二个为整数，表示分子
    # 第三个为正整数，表示分母
    # 输出：一个字符串，表示目标有理数的 p进数 表示
    r = p_adic(5, -6, 7)
    print(r)
    # 412032412032412032412032412032412032


def p_adic(p, a, b):
    # 首先依据分母确定小数点位置，然后约减分母
    t = 0
    while b % p == 0:
        t += 1
        b = b // p
    # 然后找分子对分母的整除关系，测试到一百次幂为止
    s = ''
    for k in range(40, 100):
        if (p ** k + a) % b != 0: continue
        s = trans(p, (p ** k + a) // b)
    if t > 0:
        s = s[:-t] + '.' + s[-t:]
    return s


def trans(p, x):
    tmp = ''
    while x:
        tmp = str(x % p) + tmp
        x //= p
    return tmp


main()
