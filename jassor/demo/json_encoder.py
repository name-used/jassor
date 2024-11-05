import json

import jassor.utils as J


def main():
    print('第一段描述json格式转译中字典类型key的问题(此类问题与本人工具库无关)')
    demo1()
    input('输入任意字符以继续...')
    print('第二段描述字符串转换用法')
    demo2()
    input('输入任意字符以继续...')
    print('第三段程序描述文件输出用法')
    demo3()
    input('输入任意字符以继续...')
    print('第四段程序描述细节与控制参数')
    demo4()


def demo1():
    # 对于字典格式，key 会被翻译为 str
    # 并且只有 str, int, float, bool or None 可以作为 key 出现
    # 以及，tuple 会被翻译为 list
    x = {1: 2, 3.2: (1, 2, 3, 4, 5), True: 112, None: 351}
    print(json.dumps(x))
    # {"1": 112, "3.2": 4, "null": 351}
    print(json.loads(json.dumps(x)) == x)
    # False
    # 若令 x = {'a': 1}，则为 True
    x = {'a': 1}
    print(json.loads(json.dumps(x)) == x)
    # True
    # 仅支持 ASCII 字符串书写，unicode 格式会被转译
    x = '你好世界'
    print(json.dumps(x))
    # "\u4f60\u597d\u4e16\u754c"


def demo2():
    # 本工具期望 json 转译后的格式与下列对象书写格式相仿，以便于直接阅读
    x = [
        {1: 2, 3.2: 4, True: 112, None: 351},
        [0, 1, 0, 1, 2, 'fe1', 2.5, None],
        'ppp',
        {
            'k1': [1, 2, 3, 4, 5],
            'k2': {'d': 1, 'p': 2, 'c': 3},
            'k3': 'fan das',
        }
    ]
    print(json.dumps(x))  # 没有换行，全挤在一起，什么都看不清楚，不利于阅读
    print(json.dumps(x, indent=4))  # 所有 dict、list 都换行，占用版面过大，也不利于阅读
    print(json.dumps(x, cls=J.JassorJsonEncoder))  # 最后一组容器不换行，非最后一组都换行，与上述定义格式相仿，适合阅读


def demo3():
    x = [
        {1: 2, 3.2: 4, True: 112, None: 351},
        [0, 1, 0, 1, 2, 'fe1', 2.5, None],
        'ppp',
        {
            'k1': [1, 2, 3, 4, 5],
            'k2': {'d': 1, 'p': 2, 'c': 3},
            'k3': 'fan das',
        }
    ]
    with open('./my_format.json', 'w') as f:
        json.dump(x, f, cls=J.JassorJsonEncoder)


def demo4():
    # 空数组、空列表 同样影响换行
    x = [
        ['daf', 1, None, 1.2],
        ['daf', 1, None, 1.2, []],
        ['daf', 1, None, 1.2, {}],
    ]
    print(json.dumps(x, cls=J.JassorJsonEncoder))
    # x[0] 不换行， x[1]、x[2] 均换行
    # 本工具目前只支持 indent 参数，且默认为 4，且不支持 indent=None 或 0
    print(json.dumps(x, indent=16, cls=J.JassorJsonEncoder))
    # 无论哪种格式，都可以正常读回来，且读出时不依赖本工具库
    print(x == json.loads(json.dumps(x, cls=J.JassorJsonEncoder)))
    # True
    print(x == json.loads(json.dumps(x, indent=16, cls=J.JassorJsonEncoder)))
    # True


if __name__ == '__main__':
    main()
