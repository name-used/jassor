import jassor.utils as J
import jassor.shape as S


def main():
    print('第一段程序描述基本类型')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序描述类型间变换')
    demo2()
    input('输入任意字符以继续...')
    print('第三段程序描述该库所支持的运算')
    demo3()
    input('输入任意字符以继续...')
    print('第四段程序描述图形创造器')
    demo4()
    input('输入任意字符以继续...')
    print('第五段程序描述图形结构')
    demo5()
    # shape.reversed 属性此处不做演示，其大致思路就是补集
    # 例如，c1 = Circle(0, 0, 1) 被 c2 = Circle(0, 0, 2) 完全涵盖，因此 c2.if_contain(c1) == True
    # 取 c2 的补集 ~c2，显然 c1 和 c2 完全不相交，因此有 c1.is_joint(~c2) == False
    # 补集的问题在于不方便展示，对 plot 函数的设计影响太大，大致理解其含义即可（应该是能用的吧？我没有测这个，不完全保证）


def demo1():
    region = S.Region(left=0, up=0, right=1, down=1)
    circle = S.Circle(x=0, y=0, r=1)
    simple_polygon = S.SimplePolygon(outer=[(0, 0), (1, 0), (1, 1)])
    complex_polygon = S.ComplexPolygon(outer=[(0, 0), (10, 0), (10, 10)], inners=[
        [(2, 1), (3, 1), (3, 2)], [(4, 3), (5, 3), (5, 4)], [(6, 5), (7, 5), (7, 6)]
    ])
    multi_simple_polygon = S.MultiSimplePolygon(shapes=[simple_polygon, simple_polygon + (3, 0)])
    multi_complex_polygon = S.MultiComplexPolygon(shapes=[complex_polygon, complex_polygon + (20, 0)])

    for shape in [S.EMPTY, S.FULL, region, circle, simple_polygon, complex_polygon, multi_simple_polygon, multi_complex_polygon]:
        print(shape)

    J.plots([region, circle, simple_polygon, complex_polygon, multi_simple_polygon, multi_complex_polygon])


def demo2():
    # 类型间层级关系
    region = S.Region(left=0, up=0, right=1, down=1)
    circle = S.Circle(x=0, y=0, r=1)
    for s in [region, circle]:
        assert isinstance(s, S.SimplePolygon)
        assert isinstance(s, S.ComplexPolygon)
        assert isinstance(s, S.SingleShape)
    ms = S.MultiSimplePolygon(shapes=[region, region + (3, 0)])
    assert isinstance(ms, S.MultiComplexPolygon)
    assert isinstance(ms, S.MultiShape)
    for s in [S.EMPTY, S.FULL, region, circle, ms]:
        assert isinstance(s, S.Shape)

    # 单形可以转化为任何类型
    s = circle
    print(s)
    print(S.SingleShape.asSimple(s))
    print(S.SingleShape.asComplex(s))
    print(S.SingleShape.asComplex(s))
    print(S.MultiShape.asSimple(s))
    print(S.MultiShape.asComplex(s))
    print('==========================')
    # 复形可以转化为单形，但会损失内轮廓
    s = circle >> circle / 2
    print(s)
    print(S.SingleShape.asSimple(s))
    print(S.SingleShape.asComplex(s))
    print(S.SingleShape.asComplex(s))
    print(S.MultiShape.asSimple(s))
    print(S.MultiShape.asComplex(s))
    print('==========================')
    J.plots([s, S.SingleShape.asSimple(s), S.MultiShape.asSimple(s)])

    # 多形可以转化为单形，但可能造成轮廓丢失
    # 多形转单形时有可能报 ConvertMulti2SingleException 异常
    # 该异常可以设置三种模式：mode_error(默认), mode_ignore, mode_smart
    S.ConvertMulti2SingleException.mode_ignore()
    s = (circle >> circle / 2) | circle / 2 + (2, 0)
    print(s)
    print(S.SingleShape.asSimple(s))
    print(S.SingleShape.asComplex(s))
    print(S.SingleShape.asComplex(s))
    print(S.MultiShape.asSimple(s))
    print(S.MultiShape.asComplex(s))
    J.plots([s, S.SingleShape.asSimple(s), S.SingleShape.asComplex(s), S.MultiShape.asSimple(s)])


def demo3():
    # 示例图形
    s = S.create_triangle([3, 4, 5])
    # 坐标运算
    print(s)
    print(s * 2)  # 放大
    print(s / 2)  # 缩小
    print(s + (1, 0))   # 平移
    J.plots([
        s,
        s ** 15,    # 旋转 —— 角度制
        s.copy().flip_x(x0=0),    # 水平镜像
        s.copy().flip_y(y0=0),    # 垂直镜像
        s.copy().flip(degree=45, origin=(0, 0)),  # 斜镜像
    ])
    # 集合论运算
    s = S.Circle(0, 0, 1)
    assert s.is_joint(s + (1, 0))  # 判定相交
    assert s.if_contain(s / 2)  # 判定包含
    J.plots([
        s,
        s & s + (1, 0),  # 交集运算
        s | s + (3, 0),  # 并集运算
        s << s + (3, 0),  # 合集运算，当且仅当两轮廓相交时才执行并运算
        s << s + (1, 0),  # 合集运算，当且仅当两轮廓相交时才执行并运算
        s >> s / 2,  # 差集运算
    ])

    # 形态学运算
    s = S.create_sector(radius=10, degree=30, num=100) >> S.create_regular_polygon(n=3, len_side=10) / 3 + (2, 1)
    J.plots([
        s,
        s.simplify(tolerance=0.05),  # 轮廓化简
        s.convex,   # 凸包络，
        s.mini_rect,   # 密接矩形，
        s.region,   # 矩形域，
        s.smooth(0.5),   # 平滑，
    ])

    # 几何属性
    s = S.Circle(x=0, y=0, r=1, num=1000)
    print(s)
    print(s.center)     # 形心
    print(s.area)       # 面积
    print(s.perimeter)  # 周长
    print(s.bounds)     # 矩形域


def demo4():
    # 创建正 n 边形，输入边长或外接圆半径，默认边长1
    s1 = S.create_regular_polygon(n=8, len_side=1)
    # 创建三角形，参数顺序：边角边角边角，用 None 提供缺参，确定一个三角形所需参数: SSS, SAS, AAS
    s2 = S.create_triangle(len_sides=[3, 4, 5])
    s3 = S.create_triangle(len_sides=[3, 4, None], degrees=[90, None, None])
    s4 = S.create_triangle([3, None, None], [90, 36.87, None])
    # 创建多边形，ring_close == True（默认） 时必须给定全部边角参数，且保证所给参数构成一个多边形
    s5 = S.create_polygon(len_sides=[2, 1, 1, 1.414], degrees=[90, 90, 135, 45])
    # ring_close == False 时不指定最后一个边和最后一个角
    s6 = S.create_polygon(len_sides=[2, 1, 1], degrees=[90, 90, 135], ring_close=False)
    # 创建扇形，degree < 0 时方向相反， degree ≈ 0 时返回 EMPTY，degree >= 360 时返回整圆
    s7 = S.create_sector(radius=1, degree=45)
    J.plots([s1, s2, s3, s4, s5, s6, s7])


def demo5():
    s1 = S.SingleShape.asSimple(S.Region(0, 0, 5, 5))
    s2 = S.SingleShape.asComplex(s1 >> s1 / 10 + (1, 1) >> s1 / 10 + (2, 2))
    s3 = S.MultiShape.asSimple(s1 | s1 + (10, 10))
    s4 = S.MultiShape.asComplex(s2 | s2 + (10, 10))

    # 外分解，本质是一种迭代，MultiShape -> Iterable[SingleShape]，SingleShape 也可以分解为只有自身的迭代序列
    for s in s4:
        print(s)
    for s in s1.sep_out():
        print(s)
    print('==========================')

    # 内分解，本质是将 Complex 分解为 Simple
    outer, inner = s4.sep_in()
    print(outer)
    print(inner)
    print('==========================')

    # 点分解，将图形分解为点列数组
    # outer = inner = [point] = [(x, y)]
    print(s1.sep_p())   # outer 只有一个外轮廓
    print(s2.sep_p())   # outer, inners = [inner] 一个外轮廓和一组内轮廓
    print(s3.sep_p())   # outers = [outer] 一组外轮廓
    print(s4.sep_p())   # outers, inners, adjacencies = [int] 外轮廓、内轮廓和邻接数组
    print('==========================')

    # 图像可以序列化
    shape_json = s4.dumps()
    with open('./my_shape.json', 'w') as f:
        s4.dump(f)
    with open('./my_shape.pkl', 'wb') as f:
        s4.dumpb(f)
    # 序列化后再读取
    print(S.loads(shape_json.split('\n')))
    with open('./my_shape.json', 'r') as f:
        print(S.load(f))
    with open('./my_shape.pkl', 'rb') as f:
        print(S.loadb(f))


main()
