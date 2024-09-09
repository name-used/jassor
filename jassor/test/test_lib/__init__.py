import importlib
my_modules = {
    'ActionallyBuiltifualSoup': '.module1',
    'ButNoCacheCouldBeUsed': '.module2',
}


def __getattr__(name):
    if name in my_modules:
        # print(__name__, '111111111111111111', name)
        module = importlib.import_module(my_modules[name], __package__)
        return getattr(module, name)
    else:
        raise ModuleNotFoundError('你脑瓜子被驴踢啦，我才没有这个方法呢，你给我检查清楚了再import')


__all__ = list(my_modules)
