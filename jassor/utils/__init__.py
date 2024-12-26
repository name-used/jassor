import importlib
my_modules = {
    'Logger': '.logger',
    'TimerManager': '.timer',
    'Timer': '.timer',
    'Queue': '.multiprocess',
    'Closed': '.multiprocess',
    'Process': '.multiprocess',
    'QueueMessageException': '.multiprocess',
    'JassorJsonEncoder': '.json_encoder',
    'Merger': '.merger',
    'random_colors': '.color',
    'random_rainbow_curves': '.color',
    'plot': '.jassor_plot_lib',
    'plots': '.jassor_plot_lib',
    'Table': '.table',
    'uniform_iter': '.iter_method',
    'crop': '.cropper',
}


def __getattr__(name):
    if name in my_modules:
        module = importlib.import_module(my_modules[name], __package__)
        return getattr(module, name)
    else:
        raise ModuleNotFoundError(f'The import name {name} not in this utils, check if want to import {list(my_modules.keys())}')


__all__ = list(my_modules)
