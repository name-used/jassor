# from .modnet_predict import inference as get_human
# from .classic_fg_sep import none_gray as get_none_gray, none_pure as get_none_pure, key_area as get_key_area

import importlib
my_modules = {
    'get_human': '.modnet_predict',
    'get_none_gray': '.pixel_diff',
    'get_edge': '.area_diff',
    # 'get_valid_area': '.cross_entropy',
}


def __getattr__(name):
    if name in my_modules:
        module = importlib.import_module(my_modules[name], __package__)
        return getattr(module, 'process')
    else:
        raise ModuleNotFoundError(f'The import name {name} not in this utils, check if want to import {list(my_modules.keys())}')


__all__ = list(my_modules)
