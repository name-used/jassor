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
}


def __getattr__(name):
    if name in my_modules:
        module = importlib.import_module(my_modules[name], __package__)
        return getattr(module, name)
    else:
        raise ModuleNotFoundError('你脑瓜子被驴踢啦，我才没有这个方法呢，你给我检查清楚了再 import')


__all__ = list(my_modules)
