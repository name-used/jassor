import traceback
import time
import sys
from typing import Dict, Union


class TimerManager(object):
    register = {}

    def __init__(self, container: Union[str, Dict[str, float]] = None):
        self.timers: Dict[str, Timer] = {}
        if isinstance(container, str):
            self.costs = TimerManager.register[container]
        elif container is not None:
            self.costs: Dict[str, float] = container
        else:
            self.costs: Dict[str, float] = {}

    def __getitem__(self, item: str):
        if item not in self.timers:
            self.timers[item] = Timer(item, self.costs)
        if item not in self.costs:
            self.costs[item] = 0.
        return self.timers[item]

    @staticmethod
    def stamp(t: float) -> str:
        r = f'{round(t * 1000 % 1000)}ms'
        t = int(t)
        for n, s in zip(
                [60, 60, 24, 1024],
                ['s', 'm', 'h', 'd'],
        ):
            x = t % n
            t = t // n
            r = f'{x}{s} ' + r
            if t == 0: break
        return r

    @staticmethod
    def regist_container(key: str, container: Dict[str, float]):
        TimerManager.register[key] = container


class Timer(object):
    def __init__(self, key: str, container: Union[str, Dict[str, float]]):
        self.name = key
        self.costs = container

    def __enter__(self):
        if isinstance(self.costs, str):
            self.costs = TimerManager.register[self.costs]
        if self.name not in self.costs:
            self.costs[self.name] = 0.
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            sys.stderr.write('#%s -------------------------------------- Error Message ---------------------------------------------- \n')
            sys.stderr.write(f'#%s Error: exc_type - {exc_type} \n')
            sys.stderr.write(f'#%s Error: exc_val - {exc_val} \n')
            sys.stderr.write(f'#%s Error: exc_tb - {exc_tb} \n')
            sys.stderr.write('#%s --------------------------------------------------------------------------------------------------- \n')
            sys.stderr.flush()
            traceback.print_exc()
        else:
            self.costs[self.name] += time.time() - self.start
        return False

    def __call__(self, func: callable):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper
