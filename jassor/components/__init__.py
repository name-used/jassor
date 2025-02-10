import importlib
my_modules = {
    'Marker': '.blind_mark',
    'Masking': '.create_mask',
    'data': '.data',
}


def __getattr__(name):
    if name in my_modules:
        module = importlib.import_module(my_modules[name], __package__)
        return module
    else:
        raise ModuleNotFoundError(f'The import name {name} not in this components, check if want to import {list(my_modules.keys())}')


__all__ = list(my_modules)
