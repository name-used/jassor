import importlib
my_modules = {
    'Logger': '.logger',
    'TimerManager': '.timer',
    'Timer': '.timer',
    'Queue': '.timer',
    'Closed': '.timer',
    'Process': '.timer',
    'QueueMessageException': '.timer',
    'JassorJsonEncoder': '.json_encoder',
    'Merger': '.merger',
    'random_colors': '.color',
    'random_rainbow_curves': '.color',
}


def __getattr__(name):
    if name in my_modules:
        module = importlib.import_module(my_modules[name], __package__)
        return getattr(module, name)
    else:
        raise ModuleNotFoundError('你脑瓜子被驴踢啦，我才没有这个方法呢，你给我检查清楚了再import')


__all__ = list(my_modules)


# from .logger import Logger
# from .timer import TimerManager, Timer
# from .multiprocess import Queue, Closed, Process, QueueMessageException
# from .json_encoder import JassorJsonEncoder
# from .merger import Merger
#
#
# __all__ = [
#     'Logger',
#     'TimerManager', 'Timer',
#     'Queue', 'Closed', 'Process', 'QueueMessageException',
#     'JassorJsonEncoder',
#     'Merger',
# ]
